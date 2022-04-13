import json
import os

import httpretty
import pytest
import runpy

from display import display


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


def test_average_and_standard_deviation_output(capsys):
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

    github_response = {
        "commits": [
            {
                "sha": "commit-sha1",
                "commit": {
                    "author": {"date": "2021-09-17T13:30:45Z"},
                },
            },
            {
                "sha": "commit-sha2",
                "commit": {
                    "author": {"date": "2021-09-18T13:31:45Z"},
                },
            },
            {
                "sha": "commit-sha3",
                "commit": {
                    "author": {"date": "2021-09-19T13:31:45Z"},
                },
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/test-repository/compare/0987...5678",
        body=json.dumps(github_response),
    )

    projects = [{"job": "test-job", "repository": "test-repository"}]

    display(projects)

    captured = capsys.readouterr()
    print(captured.out)
    assert "'project': 'test-repository'" in captured.out
    assert "'average': '10 days, 21:41:12.801000'" in captured.out
    assert "'standard_deviation': '19:36:09.800907'" in captured.out


