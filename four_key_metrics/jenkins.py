import requests


class Build:
    def __init__(self, started_at, finished_at, successful, environment, git_reference):
        self.started_at = started_at
        self.finished_at = finished_at
        self.successful = successful
        self.environment = environment
        self.git_reference = git_reference


def get_jenkins_builds(host, job):
    response = requests.get(
        "https://jenkins.ci.uktrade.digital/"
        "job/datahub-api/api/json",
        params={
            "tree": "builds[timestamp,result,duration,actions[parameters[*]],changeSet[items[*]]]"
        },
        headers={

        },
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