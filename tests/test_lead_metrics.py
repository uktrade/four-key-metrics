import os

import httpretty
import pytest

from four_key_metrics.presenters.lead_time_metrics import ConsolePresenter
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_github_request import httpretty_one_github_requests
from tests.mock_github_request import httpretty_three_github_requests
from tests.mock_github_request import httpretty_two_github_requests
from tests.mock_jenkins_request import httpretty_no_jenkins_builds
from tests.mock_jenkins_request import httpretty_one_jenkings_build
from tests.mock_jenkins_request import httpretty_three_jenkins_builds
from tests.mock_jenkins_request import httpretty_two_jenkins_builds
from tests.mock_jenkins_request import (
    httpretty_two_jenkins_builds_one_production_one_development,
)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["DIT_JENKINS_USER"] = "test"
    os.environ["DIT_JENKINS_TOKEN"] = "1234"
    os.environ["DIT_JENKINS_URI"] = "https://jenkins.test/"
    os.environ["GITHUB_USERNAME"] = "git_test"
    os.environ["GITHUB_TOKEN"] = "1234"
    os.environ["EXCLUDED_DEPLOYMENT_HASHES"] = '["1234"]'
    httpretty.reset()
    yield
    httpretty.disable()


class ConsoleOnlyPresenter(ConsolePresenter):
    def add(self, data: dict):
        pass

    def begin(self):
        pass

    def end(self):
        pass


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

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    assert "'project': 'test-repository'" in captured.out
    assert "'average': '60 days, 1:41:31'" in captured.out
    assert "'standard_deviation': '20:25:34.498575'" in captured.out


def test_can_get_no_lead_time(capsys):
    httpretty_no_jenkins_builds()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

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

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    print(captured.out)

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

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

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

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    print(captured.out)

    assert "'project': 'test-repository'" in captured.out
    assert "'average': '61 days, 2:42:32'" in captured.out
    assert "'standard_deviation': '0:00:00'" in captured.out


def test_can_get_lead_time_for_three_builds_one_commit(capsys):
    httpretty_three_jenkins_builds()
    httpretty_one_github_requests()
    httpretty_one_github_requests("build-sha-2", "build-sha-3")
    httpretty_one_github_requests("build-sha-1", "build-sha-3")

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    print(captured.out)

    assert "'project': 'test-repository'" in captured.out
    assert "'average': '77 days, 3:18:07.500000'" in captured.out
    assert "'standard_deviation': '16 days, 0:35:35.500000'" in captured.out


def test_can_get_lead_time_for_two_builds_two_commits(capsys):
    httpretty_two_jenkins_builds()
    httpretty_two_github_requests()

    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    print(captured.out)

    assert "'project': 'test-repository'" in captured.out
    assert "'average': '60 days, 14:12:01.500000'" in captured.out
    assert "'standard_deviation': '12:30:30.500000'" in captured.out


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
    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    assert "Not Found [404] whilst loading" in captured.out
    assert "Check your project's job name." in captured.out
