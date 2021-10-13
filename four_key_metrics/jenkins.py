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
    a = list(filter(lambda a: a.get('_class') == key, actions))
    return glom(a, Path(0, *parameter_path))


class Jenkins:

    def __init__(self, host):
        self.host = host

    def get_jenkins_builds(self, job):
        response = requests.get(
            self.host +
            "job/%s/api/json" % job,
            params={
                "tree": "builds["
                            "timestamp,result,duration,"
                            "actions["
                                "parameters[*],"
                                "lastBuiltRevision[branch[*]]"
                            "],"
                            "changeSet[items[*]]"
                        "]"
            },
            auth=(os.environ['DIT_JENKINS_USER'], os.environ['DIT_JENKINS_TOKEN'])
        )
        body = response.json()

        if len(body['builds']) == 0:
            return []

        builds = []
        for build in body['builds']:
            started_at = build['timestamp'] / 1000
            builds.append(Build(
                started_at=started_at,
                finished_at=started_at + build['duration'] / 1000,
                successful=build['result'] == 'SUCCESS',
                environment=get_action('hudson.model.ParametersAction', ['parameters', 0, 'value'], build['actions']),
                git_reference=get_action('hudson.plugins.git.util.BuildData', ['lastBuiltRevision', 'branch', 0, 'SHA1'], build['actions'])
            ))

        return builds
