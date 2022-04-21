import httpretty
import pytest
import requests
import json

from four_key_metrics.all_builds import AllBuilds


def httpretty_one_github_requests(base="build-sha-1", compare="build-sha-2"):
    github_response = {
        "commits": [
            {
                "sha": "commit-sha1",
                "commit": {
                    "author": {"date": "2022-01-01T01:01:01Z"},
                },
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/test-repository/compare/"
        + base
        + "..."
        + compare,
        body=json.dumps(github_response),
    )


def httpretty_two_github_requests(
    base="build-sha-1",
    compare="build-sha-2",
    repository="test-repository",
):
    github_response = {
        "commits": [
            {
                "sha": "commit-sha1",
                "commit": {
                    "author": {"date": "2022-01-01T01:01:01Z"},
                },
            },
            {
                "sha": "commit-sha2",
                "commit": {
                    "author": {"date": "2022-01-02T02:02:02Z"},
                },
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/" + repository + "/compare/"
        + base
        + "..."
        + compare,
        body=json.dumps(github_response),
    )


def httpretty_three_github_requests(base="build-sha-1", compare="build-sha-2"):
    github_response = {
        "commits": [
            {
                "sha": "commit-sha1",
                "commit": {
                    "author": {"date": "2022-01-01T01:01:01Z"},
                },
            },
            {
                "sha": "commit-sha2",
                "commit": {
                    "author": {"date": "2022-01-02T02:02:02Z"},
                },
            },
            {
                "sha": "commit-sha3",
                "commit": {
                    "author": {"date": "2022-01-03T03:03:03Z"},
                },
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/test-repository/compare/"
        + base
        + "..."
        + compare,
        body=json.dumps(github_response),
    )
