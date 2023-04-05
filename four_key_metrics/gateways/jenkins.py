from typing import List
import os
from glom import glom, Path
import requests

from four_key_metrics.domain_models import Build, Outage


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
                lambda b:
                    (b.environment == environment and b.successful) or 
                    (b.environment == None and b.successful),
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

    # Not all jenkins jobs have 'environment' - for many of our ones we have seperate jobs for production
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