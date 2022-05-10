import os
from datetime import datetime, timedelta
import ciso8601
import requests
from glom import glom, Path

from four_key_metrics.domain_models import Build, GitCommit, PingdomOutage


class JenkinsBuilds:
    def __init__(self, host):
        self.host = host

    def get_jenkins_builds(self, job, environment):
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

        builds = self._update_build_with_github_commits(body)
        return list(
            filter(
                lambda b: b.environment == environment,
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
        for name, id in pingdom_checks.items():
            outages = self._get_pingdom_outage_summary(id)
            for outage in outages:
                pingdom_outages.append(
                    PingdomOutage(
                        check_name=name,
                        check_id=id,
                        down_timestamp=outage["down_timestamp"],
                        up_timestamp=outage["up_timestamp"],
                    )
                )
        return pingdom_outages

