import httpretty
import pytest
import requests
import json

from four_key_metrics.all_builds import AllBuilds


def httpretty_one_github_requests(start="0987", end="5678"):
    github_response = {
        "commits": [
            {
                "sha": "commit-sha1",
                "commit": {
                    "author": {"date": "2021-09-17T13:30:45Z"},
                },
            },
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/test-repository/compare/"
        + start
        + "..."
        + end,
        body=json.dumps(github_response),
    )


def httpretty_three_github_requests(start="0987", end="5678"):
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
        "https://api.github.com/repos/uktrade/test-repository/compare/"
        + start
        + "..."
        + end,
        body=json.dumps(github_response),
    )
