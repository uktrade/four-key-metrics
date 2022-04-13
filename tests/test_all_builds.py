import json
import os

import httpretty
import pytest

from four_key_metrics.all_builds import AllBuilds
from tests.authorization_assertions import assert_authorization_is


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["DIT_JENKINS_USER"] = "test"
    os.environ["DIT_JENKINS_TOKEN"] = "1234"
    os.environ["GITHUB_USERNAME"] = "git_test"
    os.environ["GITHUB_TOKEN"] = "1234"
    os.environ["EXCLUDED_DEPLOYMENT_HASHES"] = '["1234"]'
    yield
    httpretty.reset()
    httpretty.disable()


def test_add_project():
    

    assert False


def test_can_get_no_builds():
    jenkins = {"allBuilds": []}

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.test/" "job/datahub-fe/api/json",
        body=json.dumps(jenkins),
    )

    all_builds = AllBuilds("https://jenkins.test/")
    all_builds.get_jenkins_builds("datahub-fe")

    assert len(all_builds.builds) == 0
    expected_url = (
        "https://jenkins.test/job/datahub-fe/api/json"
        "?tree=allBuilds%5Btimestamp%2Cresult%2Cduration%2C"
        "actions%5Bparameters%5B%2A%5D%2C"
        "lastBuiltRevision%5Bbranch%5B%2A%5D%5D%5D%2C"
        "changeSet%5Bitems%5B%2A%5D%5D%5D"
    )

    assert expected_url == httpretty.last_request().url
    assert_authorization_is(b"test:1234")


def test_can_get_one_build():
    jenkins = {
        "allBuilds": [
            {
                "timestamp": 1632913347701,
                "duration": 613613,
                "result": "SUCCESS",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {"name": "Environment", "value": "dev"},
                        ],
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "1234",
                                }
                            ]
                        },
                    },
                ],
            }
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/" "job/datahub-api/api/json",
        body=json.dumps(jenkins),
    )
    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")
    all_builds.get_jenkins_builds("datahub-api")

    assert len(all_builds.builds) == 1

    expected_url = (
        "https://jenkins.ci.uktrade.digital/"
        "job/datahub-api/api/json"
        "?tree=allBuilds%5Btimestamp%2Cresult%2Cduration%2C"
        "actions%5Bparameters%5B%2A%5D%2ClastBuiltRevision%5Bbranch%5B%2A%5D%5D%5D%2C"
        "changeSet%5Bitems%5B%2A%5D%5D%5D"
    )
    assert expected_url == httpretty.last_request().url

    assert all_builds.builds[0].started_at == 1632913347.701
    assert all_builds.builds[0].finished_at == 1632913961.314
    assert all_builds.builds[0].successful
    assert all_builds.builds[0].environment == "dev"
    assert all_builds.builds[0].git_reference == "1234"


def test_can_get_two_builds(capsys):
    jenkins = {
        "allBuilds": [
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "FAILURE",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {"name": "Environment", "value": "production"},
                        ],
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "0987",
                                }
                            ]
                        },
                    },
                ],
            },
            {
                "timestamp": 1632913357801,
                "duration": 600000,
                "result": "SUCCESS",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {"name": "Environment", "value": "production"},
                        ],
                    },
                    {
                        "_class": "hudson.plugins.git.util.BuildData",
                        "lastBuiltRevision": {
                            "branch": [
                                {
                                    "SHA1": "5678",
                                }
                            ]
                        },
                    },
                ],
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")
    all_builds.get_jenkins_builds("test-job")

    captured = capsys.readouterr()
    output = captured.out.replace("\\n", "\n")

    assert len(all_builds.builds) == 2
    assert all_builds.builds[0].started_at == 1632913357.801
    assert all_builds.builds[0].finished_at == 1632913957.801
    assert not all_builds.builds[0].successful
    assert all_builds.builds[0].environment == "production"
    assert all_builds.builds[0].git_reference == "0987"

    assert all_builds.builds[1].started_at == 1632913357.801
    assert all_builds.builds[1].finished_at == 1632913957.801
    assert all_builds.builds[1].successful
    assert all_builds.builds[1].environment == "production"
    assert all_builds.builds[1].git_reference == "5678"


def test_can_get_environment_from_actions_list():
    actions = [
        {
            "_class": "hudson.model.ParametersAction",
            "parameters": [
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Environment",
                    "value": "production",
                },
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Git_Commit",
                    "value": "master",
                },
            ],
        },
        {
            "_class": "hudson.plugins.git.util.BuildData",
            "lastBuiltRevision": {
                "branch": [
                    {
                        "SHA1": "9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01",
                        "name": "origin/master",
                    }
                ]
            },
        },
    ]

    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")

    sha1 = all_builds.get_action(
        "hudson.plugins.git.util.BuildData",
        ["lastBuiltRevision", "branch", 0, "SHA1"],
        actions,
    )
    assert "9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01" == sha1

    environment = all_builds.get_action(
        "hudson.model.ParametersAction", ["parameters", 0, "value"], actions
    )
    assert "production" == environment


# Show error message/hint when Jenkins times out due to lack of VPN connection.
def test_timeout_jenkins_error_message():
    assert False
