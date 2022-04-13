import os
import statistics
import pprint

import requests
from glom import glom, Path


from four_key_metrics.build import Build

# Class that extracts all builds from Jenkins based on project name.
class AllBuilds:
    def __init__(self, host):
        self.host = host
        self.builds = []
        self.lead_times = []

    def add_project(
        self, jenkins_job, github_organisation, github_repository, environment
    ):
        jenkins_builds = self._get_jenkins_builds(jenkins_job, environment)
        jenkins_builds.sort(key=lambda b: b.finished_at)
        if len(jenkins_builds) < 2:
            return {
                "successful": False,
                "lead_time_mean_average": None,
                "lead_time_standard_deviation": None,
            }

        last_build = jenkins_builds.pop(0)
        for build in jenkins_builds:
            if build.git_reference not in os.environ["EXCLUDED_DEPLOYMENT_HASHES"]:
                # Creates a GitCommit object for each commit in the build
                commits = build.get_commits_between(
                    organisation=github_organisation,
                    repository=github_repository,
                    base=last_build.git_reference,
                    head=build.git_reference,
                )
            build.set_last_build_git_reference(last_build.git_reference)
            last_build = build
        # Would be called either by AllBuilds or display.py
        # but function itself lives on Build class
        self.calculate_lead_times()
        return {
            "successful": True,
            "lead_time_mean_average": self.get_lead_time_mean_average(),
            "lead_time_standard_deviation": self.get_lead_time_standard_deviation(),
            "builds": self.builds,
        }

    def calculate_lead_times(self):
        for build in self.builds:
            for commit in build.commits:
                commit.lead_time = build.finished_at - commit.timestamp
                self.lead_times.append(commit.lead_time)
        return None

    # Will live on AllBuilds - which gets all jenkins builds and populates self.Builds
    # Would need to add the environment filtering to the all builds method
    def _get_jenkins_builds(self, jenkins_job, environment):
        jenkins_builds = self.get_jenkins_builds(jenkins_job)
        return list(filter(lambda b: b.environment == environment, jenkins_builds))

    # Would live in AllBuilds class
    def get_jenkins_builds(self, job):
        jenkins_url = self.host + "job/%s/api/json" % job
        print("all_builds.py jenkins uri: ", jenkins_url)
        response = requests.get(
            self.host + "job/%s/api/json" % job,
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
            auth=(os.environ["DIT_JENKINS_USER"], os.environ["DIT_JENKINS_TOKEN"]),
            timeout=30,
        )
        print("1")
        print(response)
        body = response.json()
        print(body)

        if len(body["allBuilds"]) == 0:
            return []

        self.builds = []
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

        # Ignore entries where no git reference present - which happens on releasing from non existing tag.
        return [build for build in self.builds if build.git_reference]

    # Would live on AllBuilds class
    def get_lead_time_mean_average(self):
        if self._no_builds():
            return None
        return sum(self.lead_times) / len(self.lead_times)

    # Would live on AllBuilds class
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
