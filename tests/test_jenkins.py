import json

import httpretty
import pytest
import os

from four_key_metrics.jenkins import Jenkins, get_action
from tests.authorization_assertions import assert_authorization_is


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ['DIT_JENKINS_USER'] = 'test'
    os.environ['DIT_JENKINS_TOKEN'] = '1234'
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

    builds = Jenkins('https://jenkins.test/').get_jenkins_builds('datahub-fe')

    assert len(builds) == 0
    expected_url = 'https://jenkins.test/job/datahub-fe/api/json' \
                   '?tree=builds%5Btimestamp%2Cresult%2Cduration%2C' \
                   'actions%5Bparameters%5B%2A%5D%2C' \
                   'lastBuiltRevision%5Bbranch%5B%2A%5D%5D%5D%2C' \
                   'changeSet%5Bitems%5B%2A%5D%5D%5D'

    assert expected_url == httpretty.last_request().url
    assert_authorization_is(b'test:1234')


def test_can_get_one_build():
    jenkins = {
        "builds": [
            {
                "timestamp": 1632913347701,
                "duration": 613613,
                "result": "SUCCESS",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "dev"
                            },
                        ]
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "1234",
                                }
                            ]
                        }
                    }
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
    builds = Jenkins('https://jenkins.ci.uktrade.digital/').get_jenkins_builds('datahub-api')

    assert len(builds) == 1

    expected_url = 'https://jenkins.ci.uktrade.digital/' \
                   'job/datahub-api/api/json' \
                   '?tree=builds%5Btimestamp%2Cresult%2Cduration%2C' \
                   'actions%5Bparameters%5B%2A%5D%2ClastBuiltRevision%5Bbranch%5B%2A%5D%5D%5D%2C' \
                   'changeSet%5Bitems%5B%2A%5D%5D%5D'
    assert expected_url == httpretty.last_request().url

    assert builds[0].started_at == 1632913347.701
    assert builds[0].finished_at == 1632913961.314
    assert builds[0].successful
    assert builds[0].environment == 'dev'
    assert builds[0].git_reference == '1234'


def test_can_get_two_builds():
    jenkins = {
        "builds": [
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "FAILURE",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "production"
                            },
                        ]
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "0987",
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "SUCCESS",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {
                                "name": "Environment",
                                "value": "production"
                            },
                        ]
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "5678",
                                }
                            ]
                        }
                    }
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
    builds = Jenkins('https://jenkins.ci.uktrade.digital/').get_jenkins_builds('datahub-api')

    assert len(builds) == 2
    assert builds[0].started_at == 1632913357.801
    assert builds[0].finished_at == 1632913957.801
    assert not builds[0].successful
    assert builds[0].environment == 'production'
    assert builds[0].git_reference == '0987'

    assert builds[1].started_at == 1632913357.801
    assert builds[1].finished_at == 1632913957.801
    assert builds[1].successful
    assert builds[1].environment == 'production'
    assert builds[1].git_reference == '5678'


def test_can_get_environment_from_actions_list():
    actions = [
        {
            "_class": "hudson.model.ParametersAction",
            "parameters": [
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Environment",
                    "value": "production"
                },
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Git_Commit",
                    "value": "master"
                }
            ]
        },
        {
            "_class": "hudson.plugins.git.util.BuildData",
            "lastBuiltRevision": {
                "branch": [
                    {
                        "SHA1": "9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01",
                        "name": "origin/master"
                    }
                ]
            }
        }
    ]

    sha1 = get_action('hudson.plugins.git.util.BuildData', ['lastBuiltRevision', 'branch', 0, 'SHA1'], actions)
    assert '9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01' == sha1

    environment = get_action('hudson.model.ParametersAction', ['parameters', 0, 'value'], actions)
    assert 'production' == environment