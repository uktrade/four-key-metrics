import os
import pytest
import httpretty

from four_key_metrics.gateways import CircleCiRuns
from tests.mock_circle_ci_request import (
    httpretty_404_not_found_circle_ci_runs,
    httpretty_circle_ci_no_runs,
    httpretty_circle_ci_runs_success,
    two_mock_runs,
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

    expected_result = two_mock_runs
    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == expected_result


def test_get_circle_ci_runs_no_items():
    httpretty_circle_ci_no_runs()

    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == []


def test_get_circle_ci_runs_not_found(capsys):
    httpretty_404_not_found_circle_ci_runs()
    circle_ci_runs = CircleCiRuns().get_circle_ci_runs(
        "test-wrong-project", "test-workflow"
    )
    captured = capsys.readouterr()

    assert "Check your project or workflow name" in captured.out
    assert (
        "Not Found [404] whilst loading https://circleci.com/api/v2/insights/test-wrong-project/workflows/test-workflow"
        in captured.out
    )
    assert circle_ci_runs == []
