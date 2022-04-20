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
                "timestamp": 1643768542000,
                "duration": 613613,
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
        "https://jenkins.test/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    all_builds = AllBuilds("https://jenkins.test/")
    return all_builds


def httpretty_two_jenkins_builds():
    jenkins = {
        "allBuilds": [
            {
                "timestamp": 1643768542000,
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
                                    "SHA1": "build-sha-1",
                                }
                            ]
                        },
                    },
                ],
            },
            {
                "timestamp": 1646278413000,
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
                                    "SHA1": "build-sha-2",
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
        "https://jenkins.test/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    return AllBuilds("https://jenkins.test/")


def httpretty_two_jenkins_builds_one_production_one_development():
    jenkins = {
        "allBuilds": [
            {
                "timestamp": 1643768542000,
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
                "timestamp": 1646278413000,
                "duration": 600000,
                "result": "SUCCESS",
                "actions": [
                    {
                        "_class": "hudson.model.ParametersAction",
                        "parameters": [
                            {"name": "Environment", "value": "development"},
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
        "https://jenkins.test/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    return AllBuilds("https://jenkins.test/")


def httpretty_three_jenkins_builds():
    jenkins = {
        "allBuilds": [
            {
                "timestamp": 1643768542000,
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
                                    "SHA1": "build-sha-1",
                                }
                            ]
                        },
                    },
                ],
            },
            {
                "timestamp": 1646278413000,
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
                                    "SHA1": "build-sha-2",
                                }
                            ]
                        },
                    },
                ],
            },
            {
                "timestamp": 1649047484000,
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
                                    "SHA1": "build-sha-3",
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
        "https://jenkins.test/" "job/test-job/api/json",
        body=json.dumps(jenkins),
    )
    return AllBuilds("https://jenkins.test/")
