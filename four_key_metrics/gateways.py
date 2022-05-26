import os
from datetime import datetime, timedelta
from typing import List
import ciso8601
import requests
from glom import glom, Path

from four_key_metrics.domain_models import Build, GitCommit, Outage
from four_key_metrics.utilities import iso_string_to_timestamp


class JenkinsBuilds:
    def __init__(self, host):
        self.host = host

    def get_jenkins_builds(self, job):
        try:
            jenkins_url = self.host + "job/%s/api/json" % job
            response = requests.get(
                jenkins_url,
                params={
                    "tree": "allBuilds["
                    "timestamp,result,duration,"
                    "actions["
                    "parameters[*],"
                    "lastBuiltRevision[branch[*]]"
                    "],"
                    "changeSet[items[*]]"
                    "]"
                },
                auth=(
                    os.environ["DIT_JENKINS_USER"],
                    os.environ["DIT_JENKINS_TOKEN"],
                ),
                timeout=5,
            )
        except requests.exceptions.ConnectionError as connect_timeout:
            print(connect_timeout.args[0])
            print("Are you connected to the VPN‽")
            return []

        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your project's job name.")
            return []

        body = response.json()
        if len(body["allBuilds"]) == 0:
            return []

        return self._update_build_with_github_commits(body)

    def get_successful_production_builds(self, job, environment):
        builds = self.get_jenkins_builds(job)
        return list(
            filter(
                lambda b: b.environment == environment and b.successful,
                [build for build in builds if build.git_reference],
            )
        )

    def _update_build_with_github_commits(self, body):
        builds = []
        for build in body["allBuilds"]:
            started_at = build["timestamp"] / 1000
            builds.append(
                Build(
                    started_at=started_at,
                    finished_at=started_at + build["duration"] / 1000,
                    successful=build["result"] == "SUCCESS",
                    environment=self._get_environment(build),
                    git_reference=self._get_git_reference(build),
                )
            )
        return builds

    def _get_git_reference(self, build):
        return self.get_action(
            "hudson.plugins.git.util.BuildData",
            ["lastBuiltRevision", "branch", 0, "SHA1"],
            build["actions"],
        )

    def _get_environment(self, build):
        return self.get_action(
            "hudson.model.ParametersAction",
            ["parameters", 0, "value"],
            build["actions"],
        )

    def get_action(self, key, parameter_path, actions):
        a = list(filter(lambda a: a.get("_class") == key, actions))
        if a:
            return glom(a, Path(0, *parameter_path))
        else:
            return None

    def get_jenkins_outages(self, jenkins_jobs):
        outages = []
        for job in jenkins_jobs:
            builds = self.get_jenkins_builds(job)
            grouped_builds = self.group_builds_by_environment(builds)
            for environment, builds in grouped_builds.items():
                outages.extend(
                    self.create_outages_for_environment(environment, builds, job)
                )
        return outages

    def group_builds_by_environment(self, builds):
        envs_dict = {
            environment: []
            for environment in set(build.environment for build in builds)
        }
        for build in builds:
            envs_dict[build.environment].append(build)
        return envs_dict

    def order_builds_by_ascending_timestamp(self, builds):
        return sorted(builds, key=(lambda build: build.started_at))

    def create_outages_for_environment(
        self, environment, builds, jenkins_job
    ) -> List[Outage]:
        outages = []
        build_started_outage = None
        ordered_builds = self.order_builds_by_ascending_timestamp(builds)
        for build in ordered_builds:
            if not build.successful and not build_started_outage:
                # store the failed build that marks the start of an outage
                build_started_outage = build
            elif build.successful and build_started_outage:
                outages.append(
                    Outage(
                        source="jenkins",
                        environment=environment,
                        project=jenkins_job,
                        jenkins_failed_build_hash=build_started_outage.git_reference,
                        down_timestamp=round(build_started_outage.started_at),
                        up_timestamp=round(build.finished_at),
                    )
                )
                build_started_outage = None
            else:
                pass
        return outages


class GitHubCommits:
    def get_commits_between(self, organisation, repository, base, head):
        response = requests.get(
            "https://api.github.com/repos/%s/%s/compare/%s...%s?per_page=10000"
            % (organisation, repository, base, head),
            auth=(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_TOKEN"]),
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=30,
        )

        commits = []
        for commit in response.json()["commits"]:
            commit_author_date = commit["commit"]["author"]["date"]
            timestamp = ciso8601.parse_datetime(commit_author_date).timestamp()
            commits.append(GitCommit(sha=commit["sha"], timestamp=timestamp))
        return commits


class PingdomOutages:
    def _get_pingdom_id_for_check_names(self, pingdom_check_names):
        response = requests.get(
            "https://api.pingdom.com/api/3.1/checks/",
            headers={"Authorization": "Bearer " + (os.environ["PINGDOM_TOKEN"])},
            timeout=5,
        )
        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your project's job name.")
            return {}

        body = response.json()
        if len(body["checks"]) == 0:
            return {}

        check_ids = {
            check["name"]: check["id"]
            for check in body["checks"]
            if check["name"] in pingdom_check_names
        }

        if len(check_ids) != len(pingdom_check_names):
            print("WARNING: Not all Pingdom checks found. Check for typos.")

        return check_ids

    def _get_pingdom_outage_summary(self, pingdom_check_id, from_timestamp=None):
        if not from_timestamp:
            from_timestamp = int(
                datetime.timestamp(datetime.now() - timedelta(days=180))
            )
        response = requests.get(
            f"https://api.pingdom.com/api/3.1/summary.outage/{pingdom_check_id}?from={from_timestamp}",
            headers={"Authorization": "Bearer " + (os.environ["PINGDOM_TOKEN"])},
            timeout=5,
        )
        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your pingdom check id.")
            return {}

        body = response.json()

        return [
            {"down_timestamp": outage["timefrom"], "up_timestamp": outage["timeto"]}
            for outage in body["summary"]["states"]
            if outage["status"] == "down"
        ]

    def get_pingdom_outages(self, pingdom_check_names):
        pingdom_outages = []
        pingdom_checks = self._get_pingdom_id_for_check_names(pingdom_check_names)
        for name, pingdom_check_id in pingdom_checks.items():
            outages = self._get_pingdom_outage_summary(pingdom_check_id)
            for outage in outages:
                pingdom_outages.append(
                    Outage(
                        source="pingdom",
                        environment="production",
                        project=name,
                        pingdom_check_id=pingdom_check_id,
                        down_timestamp=outage["down_timestamp"],
                        up_timestamp=outage["up_timestamp"],
                    )
                )
        return pingdom_outages


class CircleCiRuns:
    def _get_circle_ci_runs(self, project, workflow) -> List[dict]:

        response = requests.get(
            f"https://circleci.com/api/v2/insights/{project}/workflows/{workflow}",
            headers={"Authorization": "Bearer " + (os.environ["CIRCLE_CI_TOKEN"])},
            timeout=5,
        )

        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your project or workflow name")
            return []

        body = response.json()
        return body["items"]

    def _sort_runs_by_ascending_time(self, runs) -> List[dict]:
        return sorted(runs, key=(lambda run: run["created_at"]))

    def get_circle_ci_outages(self, project, workflow) -> List[Outage]:
        runs = self._get_circle_ci_runs(project, workflow)
        ascending_runs = self._sort_runs_by_ascending_time(runs)
        outages = []
        failed_run_starting_outage = None
        for run in ascending_runs:

            is_succcessful_run = run["status"] == "success"

            if not is_succcessful_run and not failed_run_starting_outage:
                failed_run_starting_outage = run

            elif is_succcessful_run and failed_run_starting_outage:
                outages.append(
                    Outage(
                        source="circle_ci",
                        project=project,
                        environment=run["branch"],
                        circle_ci_failed_run_id=failed_run_starting_outage["id"],
                        down_timestamp=round(
                            iso_string_to_timestamp(
                                failed_run_starting_outage["created_at"]
                            )
                        ),
                        up_timestamp=round(iso_string_to_timestamp(run["stopped_at"])),
                    )
                )
                failed_run_starting_outage = None
            else:
                pass
        return outages
