import os

import requests


class Build:
    def __init__(self, started_at, finished_at, successful, environment, git_reference):
        self.started_at = started_at
        self.finished_at = finished_at
        self.successful = successful
        self.environment = environment
        self.git_reference = git_reference


class Jenkins:

    def __init__(self, host):
        self.host = host

    def get_jenkins_builds(self, job):
        response = requests.get(
            self.host +
            "job/%s/api/json" % job,
            params={
                "tree": "builds[timestamp,result,duration,actions[parameters[*]],changeSet[items[*]]]"
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
                environment=build['actions'][0]['parameters'][0]['value'],
                git_reference=build['actions'][0]['parameters'][1]['value']
            ))
        return builds
