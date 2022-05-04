import json
import os

import httpretty
import pytest

from four_key_metrics.domain_models import Build
from four_key_metrics.gateways import GitHubCommits
from tests.authorization_assertions import assert_authorization_is


# class TestBuild:
@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["GITHUB_USERNAME"] = "testing"
    os.environ["GITHUB_TOKEN"] = "5678"
    httpretty.reset()
    yield
    httpretty.disable()


def test_can_get_comparison_with_one_commit():
    github_response = {
        "commits": [
            {
                "sha": "commit-sha",
                "commit": {
                    "author": {"date": "2021-09-17T13:30:45Z"},
                },
            }
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/data-hub-frontend/compare/v9.19.0...v9.17.1",
        body=json.dumps(github_response),
    )

    build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful="SUCCESS",
        environment="testing",
        git_reference="sha1-git-reference",
    )

    commits = GitHubCommits().get_commits_between(
        organisation="uktrade",
        repository="data-hub-frontend",
        base="v9.19.0",
        head="v9.17.1",
    )

    assert len(commits) == 1
    assert commits[0].timestamp == 1631885445.0
    assert commits[0].sha == "commit-sha"


def test_can_get_comparison_with_two_commits():
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
        ]
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/uktrade/data-hub-frontend/compare/v9.19.0...v9.17.1",
        body=json.dumps(github_response),
    )

    build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful="SUCCESS",
        environment="testing",
        git_reference="sha1-git-reference",
    )

    commits = GitHubCommits().get_commits_between(
        organisation="uktrade",
        repository="data-hub-frontend",
        base="v9.19.0",
        head="v9.17.1",
    )

    assert len(commits) == 2
    assert commits[0].timestamp == 1631885445.0
    assert commits[0].sha == "commit-sha1"
    assert commits[1].timestamp == 1631971905.0
    assert commits[1].sha == "commit-sha2"


def test_can_request_different_comparisons():
    github_response = {"commits": []}

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/123/456/compare/789...0",
        body=json.dumps(github_response),
    )

    build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful="SUCCESS",
        environment="testing",
        git_reference="sha1-git-reference",
    )

    GitHubCommits().get_commits_between(
        organisation="123",
        repository="456",
        base="789",
        head="0",
    )

    assert (
        httpretty.last_request().url
        == "https://api.github.com/repos/123/456/compare/789...0?per_page=10000"
    )


def test_can_use_authentication():
    github_response = {"commits": []}

    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/123/456/compare/789...0",
        body=json.dumps(github_response),
    )

    build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful="SUCCESS",
        environment="testing",
        git_reference="sha1-git-reference",
    )

    GitHubCommits().get_commits_between(
        organisation="123",
        repository="456",
        base="789",
        head="0",
    )

    assert_authorization_is(b"testing:5678")


def test_set_last_build_git_reference():
    build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful="SUCCESS",
        environment="testing",
        git_reference="sha1-git-reference",
    )

    build.set_last_build_git_reference("last_build_git_reference")

    assert build.last_build_git_reference == "last_build_git_reference"
