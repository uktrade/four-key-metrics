import os
import pytest
import httpretty

from four_key_metrics.gateways import CircleCiRuns
from tests.mock_circle_ci_request import (
    httpretty_404_not_found_circle_ci_runs,
    httpretty_circle_ci_no_runs,
    httpretty_circle_ci_runs_success,
)

@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["CIRCLE_CI_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()

def xtest_get_circle_ci_runs_success():
    httpretty_circle_ci_runs_success()

    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs

def test_get_circle_ci_runs_no_items():
    httpretty_circle_ci_no_runs()
    
    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == []
    

def xtest_get_circle_ci_runs_not_found():
    httpretty_404_not_found_circle_ci_runs()

    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-wrong-project", "test-workflow")
    assert circle_ci_runs
    

