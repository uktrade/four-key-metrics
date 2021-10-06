import json

import httpretty
import pytest

from four_key_metrics.jenkins import get_jenkins_builds as _gjb


def get_jenkins_builds(host, job):
    return _gjb(host, job)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    yield
    httpretty.reset()
    httpretty.disable()


def test_can_get_no_builds():
    jenkins = {
        "builds": []
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.test/"
        "job/datahub-fe/api/json",
        body=json.dumps(jenkins)
    )

    builds = get_jenkins_builds('https://jenkins.test/', 'datahub-fe')

    assert len(builds) == 0
    expected_url = 'https://jenkins.test/' \
                   'job/datahub-fe/api/json' \
                   '?tree=builds%5Btimestamp%2Cresult%2Cduration%2Cactions%5Bparameters' \
                   '%5B%2A%5D%5D%2CchangeSet%5Bitems%5B%2A%5D%5D%5D'
    assert expected_url == httpretty.last_request().url


def test_can_get_one_build():
    jenkins = {
        "builds": [
            {
                "timestamp": 1632913347701,
                "duration": 613613,
                "result": "SUCCESS",
                "actions": [
                    {
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "dev"
                            },
                            {
                                "name": "Git_Commit",
                                "value": "main"
                            }
                        ]
                    },
                ]
            }
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/"
        "job/datahub-api/api/json",
        body=json.dumps(jenkins)
    )
    builds = get_jenkins_builds('https://jenkins.ci.uktrade.digital/', 'datahub-api')

    assert len(builds) == 1

    expected_url = 'https://jenkins.ci.uktrade.digital/' \
                   'job/datahub-api/api/json' \
                   '?tree=builds%5Btimestamp%2Cresult%2Cduration%2Cactions%5Bparameters' \
                   '%5B%2A%5D%5D%2CchangeSet%5Bitems%5B%2A%5D%5D%5D'
    assert expected_url == httpretty.last_request().url

    assert builds[0].started_at == 1632913347.701
    assert builds[0].finished_at == 1632913961.314
    assert builds[0].successful
    assert builds[0].environment == 'dev'
    assert builds[0].git_reference == 'main'


def test_can_get_two_builds():
    jenkins = {
        "builds": [
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "FAILURE",
                "actions": [
                    {
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "production"
                            },
                            {
                                "name": "Git_Commit",
                                "value": "v1.0"
                            }
                        ]
                    },
                ]
            },
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "SUCCESS",
                "actions": [
                    {
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "production"
                            },
                            {
                                "name": "Git_Commit",
                                "value": "v1.1"
                            }
                        ]
                    },
                ]
            }
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/"
        "job/datahub-api/api/json",
        body=json.dumps(jenkins)
    )
    builds = get_jenkins_builds('https://jenkins.ci.uktrade.digital/', 'datahub-api')

    assert len(builds) == 2
    assert builds[0].started_at == 1632913357.801
    assert builds[0].finished_at == 1632913957.801
    assert not builds[0].successful
    assert builds[0].environment == 'production'
    assert builds[0].git_reference == 'v1.0'

    assert builds[1].started_at == 1632913357.801
    assert builds[1].finished_at == 1632913957.801
    assert builds[1].successful
    assert builds[1].environment == 'production'
    assert builds[1].git_reference == 'v1.1'

