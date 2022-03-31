import os

import requests
from glom import glom, Path


class Build:
    def __init__(self, started_at, finished_at, successful, environment, git_reference):
        self.started_at = started_at
        self.finished_at = finished_at
        self.successful = successful
        self.environment = environment
        self.git_reference = git_reference


def get_action(key, parameter_path, actions):
    a = list(filter(lambda a: a.get("_class") == key, actions))
    if a:
        return glom(a, Path(0, *parameter_path))
    else:
        return None


class Jenkins:
    def __init__(self, host):
        self.host = host

    def get_jenkins_builds(self, job):
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
        body = response.json()

        if len(body["allBuilds"]) == 0:
            return []

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

        # Ignore entries where no git reference present - which happens on releasing from non existing tag.
        return [build for build in builds if build.git_reference]

    def _get_git_reference(self, build):
        return get_action(
            "hudson.plugins.git.util.BuildData",
            ["lastBuiltRevision", "branch", 0, "SHA1"],
            build["actions"],
        )

    def _get_environment(self, build):
        return get_action(
            "hudson.model.ParametersAction",
            ["parameters", 0, "value"],
            build["actions"],
        )
