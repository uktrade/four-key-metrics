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

    print(
        "test_display.py@register_uri: ",
        "https://jenkins.ci.uktrade.digital/",
        "job/test-job/api/json",
    )

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.ci.uktrade.digital/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )

    print(
        "test_display.py@register_uri: ",
        "https://api.github.com/repos/uktrade/data-hub-frontends/compare/0987...5678",
    )

    # httpretty.register_uri(
    #     httpretty.GET,
    #     "https://api.github.com/repos/uktrade/data-hub-frontends/compare/0987...5678",
    #     body=json.dumps(github_response),
    # )

    #    projects =

    # override projects array

    display([{"job": "test-job", "repository": "test-repository"}])

    captured = capsys.readouterr()
    print(captured.out)
    # assert captured.out == "hello\n"
    # call 'display.py'

    #    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")
    #    all_builds.get_jenkins_builds("datahub-api")

    # Create and insert dummy input
    # Assert output
    # output = {
    #     "average": "4 days, 10:11:19.988286",
    #     "project": "data-hub-frontend",
    #     "standard_deviation": "4 days, 23:57:23.917895",
    # }
    # assert True


# def test_can_get_jenkins_builds(authentication):
#     basic_string = base64.b64encode(authentication).decode()
#     actual_header = httpretty.last_request().headers["Authorization"]
#     expected_header = "Basic %s" % basic_string
#     assert actual_header == expected_header
