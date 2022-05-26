import os
import pytest
import httpretty
from four_key_metrics.domain_models import Outage

from four_key_metrics.gateways import CircleCiRuns
from tests.mock_circle_ci_request import (
    httpretty_401_unauthorized_circle_ci_runs,
    httpretty_404_not_found_circle_ci_runs,
    httpretty_circle_ci_no_runs,
    httpretty_circle_ci_runs_success,
    four_mock_runs,
)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["CIRCLE_CI_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_get_circle_ci_runs_success():
    httpretty_circle_ci_runs_success()

    expected_result = four_mock_runs
    circle_ci_runs = CircleCiRuns()._get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == expected_result


def test_get_circle_ci_runs_no_items():
    httpretty_circle_ci_no_runs()

    circle_ci_runs = CircleCiRuns()._get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == []


def test_get_circle_ci_runs_not_found(capsys):
    httpretty_404_not_found_circle_ci_runs()
    circle_ci_runs = CircleCiRuns()._get_circle_ci_runs(
        "test-wrong-project", "test-workflow"
    )
    captured = capsys.readouterr()

    assert "Check your project or workflow name" in captured.out
    assert (
        "Not Found [404] whilst loading https://circleci.com/api/v2/insights/test-wrong-project/workflows/test-workflow"
        in captured.out
    )
    assert circle_ci_runs == []


def test_get_circle_ci_runs_unauthorized(capsys):
    httpretty_401_unauthorized_circle_ci_runs()
    circle_ci_runs = CircleCiRuns()._get_circle_ci_runs(
        "test-wrong-project", "test-workflow"
    )
    captured = capsys.readouterr()
    assert (
        "Unauthorized [401] whilst loading https://circleci.com/api/v2/insights/test-wrong-project/workflows/test-workflow"
        in captured.out
    )
    assert circle_ci_runs == []


def test_sort_runs_by_ascending_time():
    expected_result = [
        {
            "id": "89ad3361-99eb-44a4-8c97-03c0b62eb3f2",
            "duration": 731,
            "status": "failed",
            "created_at": "2022-05-20T10:13:58.411Z",
            "stopped_at": "2022-05-20T10:26:09.509Z",
            "credits_used": 25165,
            "branch": "master",
            "is_approval": "false",
        },
        {
            "id": "79ad3361-99eb-44a4-8c97-03c0b62eb3f2",
            "duration": 731,
            "status": "success",
            "created_at": "2022-05-22T10:13:58.411Z",
            "stopped_at": "2022-05-22T10:26:09.509Z",
            "credits_used": 25165,
            "branch": "master",
            "is_approval": "false",
        },
        {
            "id": "69ad3361-99eb-44a4-8c97-03c0b62eb3f2",
            "duration": 731,
            "status": "failed",
            "created_at": "2022-05-23T10:13:58.411Z",
            "stopped_at": "2022-05-23T10:26:09.509Z",
            "credits_used": 25165,
            "branch": "master",
            "is_approval": "false",
        },
        {
            "id": "59ad3361-99eb-44a4-8c97-03c0b62eb3f2",
            "duration": 731,
            "status": "success",
            "created_at": "2022-05-24T10:13:58.411Z",
            "stopped_at": "2022-05-24T10:26:09.509Z",
            "credits_used": 25165,
            "branch": "master",
            "is_approval": "false",
        },
    ]

    sorted_runs = CircleCiRuns()._sort_runs_by_ascending_time(four_mock_runs)
    assert sorted_runs == expected_result


def test_get_circle_ci_outages_success():
    httpretty_circle_ci_runs_success()

    expected_result = [
        Outage(
            source="circle_ci",
            project="test-project",
            environment="master",
            down_timestamp=1653041638,
            up_timestamp=1653215170,
            circle_ci_failed_run_id="89ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        ),
        Outage(
            source="circle_ci",
            project="test-project",
            environment="master",
            down_timestamp=1653300838,
            up_timestamp=1653387970,
            circle_ci_failed_run_id="69ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        ),
    ]

    circle_ci_outages = CircleCiRuns().get_circle_ci_outages(
        "test-project", "test-workflow"
    )

    assert circle_ci_outages[0].__dict__ == expected_result[0].__dict__
    assert circle_ci_outages[1].__dict__ == expected_result[1].__dict__


def xtest_get_circle_ci_outages_failure():
    # test return empty list
    pass
