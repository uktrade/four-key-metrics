import os
import statistics
import requests
from glom import glom, Path


from four_key_metrics.build import Build

class UseCaseyCode:
    """temporary location for code that really belongs in a use case not here"""

    def __init__(self, all_builds):
        self._all_builds = all_builds

    def add_project(
        self, jenkins_job, github_organisation, github_repository, environment
    ):
        jenkins_builds = self._all_builds.get_jenkins_builds(jenkins_job, environment)
        jenkins_builds.sort(key=lambda b: b.finished_at)
        if len(jenkins_builds) < 2:
            return self._build_summary()
        self._update_last_build_git_reference(
            github_organisation, github_repository, jenkins_builds
        )
        self.calculate_lead_times()
        return self._build_summary(
            True,
            self._all_builds.get_lead_time_mean_average(),
            self._all_builds.get_lead_time_standard_deviation(),
            self._all_builds.builds,
        )

    def calculate_lead_times(self):
        for build in self._all_builds.builds:
            for commit in build.commits:
                commit.lead_time = build.finished_at - commit.timestamp
                self._all_builds.lead_times.append(commit.lead_time)
        return None

    def _update_last_build_git_reference(
        self,
        github_organisation,
        github_repository,
        jenkins_builds,
    ):
        last_build = jenkins_builds.pop(0)
        excluded_hashes = os.environ["EXCLUDED_DEPLOYMENT_HASHES"]
        for build in jenkins_builds:
            self._update_with_exclusion_builds_with_git_reference(
                github_organisation,
                github_repository,
                last_build,
                excluded_hashes,
                build,
            )
            last_build = build

    def _update_with_exclusion_builds_with_git_reference(
        self, github_organisation, github_repository, last_build, excluded_hashes, build
    ):
        if build.git_reference not in excluded_hashes:
            build.get_commits_between(
                organisation=github_organisation,
                repository=github_repository,
                base=last_build.git_reference,
                head=build.git_reference,
            )
        build.set_last_build_git_reference(last_build.git_reference)

    def _build_summary(
        self,
        is_success: bool = False,
        lead_time_mean_average: str | None = None,
        lead_time_standard_deviation: str | None = None,
        builds: list = None,
    ):
        return {
            "successful": is_success,
            "lead_time_mean_average": lead_time_mean_average,
            "lead_time_standard_deviation": lead_time_standard_deviation,
            "builds": builds,
        }


class AllBuilds:
    def __init__(self, host):
        self.host = host
        self.builds = []
        self.lead_times = []

    def add_project(
        self, jenkins_job, github_organisation, github_repository, environment
    ):
        return UseCaseyCode(self).add_project(jenkins_job, github_organisation, github_repository, environment)

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

        self.builds = []
        self._update_build_with_github_commits(body)
        return list(
            filter(
                lambda b: b.environment == environment,
                [build for build in self.builds if build.git_reference],
            )
        )

    def _update_build_with_github_commits(self, body):
        for build in body["allBuilds"]:
            started_at = build["timestamp"] / 1000
            self.builds.append(
                Build(
                    started_at=started_at,
                    finished_at=started_at + build["duration"] / 1000,
                    successful=build["result"] == "SUCCESS",
                    environment=self._get_environment(build),
                    git_reference=self._get_git_reference(build),
                )
            )

    def get_lead_time_mean_average(self):
        if self._no_builds():
            return None
        return sum(self.lead_times) / len(self.lead_times)

    def get_lead_time_standard_deviation(self):
        if self._no_builds():
            return None
        return statistics.pstdev(self.lead_times)

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

    def _no_builds(self) -> bool:
        return len(self.builds) == 0
