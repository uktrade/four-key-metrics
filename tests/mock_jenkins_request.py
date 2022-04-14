import httpretty
import pytest
import requests
import json

from four_key_metrics.all_builds import AllBuilds


def httpretty_404_no_job_jenkings_builds():
    httpretty.register_uri(
        httpretty.GET, "https://jenkins.test/" "job//api/json", status=404
    )
    return


def httpretty_no_jenkings_builds():
    jenkins = {"allBuilds": []}

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.test/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )

    all_builds = AllBuilds("https://jenkins.test/")
    return all_builds


def httpretty_one_jenkings_build():
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
        "https://jenkins.ci.uktrade.digital/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")
    return all_builds


def httpretty_two_jenkins_builds():
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
    return AllBuilds("https://jenkins.ci.uktrade.digital/")
