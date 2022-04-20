import json
import os

import httpretty
import pytest
import runpy

from display import display

from tests.mock_jenkins_request import httpretty_404_no_job_jenkings_builds
from tests.mock_jenkins_request import httpretty_no_jenkings_builds
from tests.mock_jenkins_request import httpretty_one_jenkings_build
from tests.mock_jenkins_request import httpretty_two_jenkins_builds
from tests.mock_jenkins_request import (
    httpretty_two_jenkins_builds_one_production_one_development,
)
from tests.mock_github_request import httpretty_one_github_requests
from tests.mock_github_request import httpretty_three_github_requests


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["DIT_JENKINS_USER"] = "test"
    os.environ["DIT_JENKINS_TOKEN"] = "1234"
    os.environ["DIT_JENKINS_URI"] = "https://jenkins.test/"
    os.environ["GITHUB_USERNAME"] = "git_test"
    os.environ["GITHUB_TOKEN"] = "1234"
    os.environ["EXCLUDED_DEPLOYMENT_HASHES"] = '["1234"]'
    yield
    httpretty.reset()
    httpretty.disable()


def test_average_and_standard_deviation_output(capsys):
    httpretty_two_jenkins_builds()
    httpretty_three_github_requests()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    display(projects)

    captured = capsys.readouterr()
    assert "'project': 'test-repository'" in captured.out
    assert "'average': '10 days, 21:41:12.801000'" in captured.out
    assert "'standard_deviation': '19:36:09.800907'" in captured.out


def test_can_get_no_lead_time(capsys):
    httpretty_no_jenkings_builds()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    display(projects)

    captured = capsys.readouterr()
    assert "'project': 'test-repository'" in captured.out


def test_can_not_get_lead_time_for_one_build(capsys):
    httpretty_one_jenkings_build()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    display(projects)

    captured = capsys.readouterr()
    print(captured.out)
    # TODO Check why no data returned.
    assert "'project': 'test-repository'" in captured.out
    assert "'average': None" in captured.out
    assert "'standard_deviation': None" in captured.out


def test_can_not_get_lead_time_for_mismatched_environments(capsys):
    httpretty_two_jenkins_builds_one_production_one_development()
    httpretty_three_github_requests()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    display(projects)

    captured = capsys.readouterr()
    print(captured.out)

    assert "'project': 'test-repository'" in captured.out
    assert "'average': None" in captured.out
    assert "'standard_deviation': None" in captured.out


def test_can_get_lead_time_for_two_builds_one_commit(capsys):
    httpretty_two_jenkins_builds()
    httpretty_one_github_requests()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    display(projects)

    captured = capsys.readouterr()
    print(captured.out)

    assert "'project': 'test-repository'" in captured.out
    assert "'average': '11 days, 21:41:52.801000'" in captured.out
    assert "'standard_deviation': '0:00:00'" in captured.out


def test_can_get_lead_time_for_three_builds_one_commit():
    assert "TODO"


def test_project_job_not_found(capsys):
    httpretty.register_uri(
        httpretty.GET,
        os.environ["DIT_JENKINS_URI"] + "job/test-job/api/json",
        status=404,
    )
    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]
    display(projects)

    captured = capsys.readouterr()
    assert "Not Found [404] whilst loading" in captured.out
    assert "Check your project's job name." in captured.out
