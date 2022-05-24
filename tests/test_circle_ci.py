import os
import pytest
import httpretty

from four_key_metrics.gateways import CircleCiRuns
from tests.mock_circle_ci_request import (
    httpretty_no_circle_ci_runs,
)

@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["CIRCLE_CI_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()

def test_get_circle_ci_runs_success():
    pass

def test_get_circle_ci_runs_no_items():
    httpretty_no_circle_ci_runs()
    
    circle_ci_runs = CircleCiRuns().get_circle_ci_runs("test-project", "test-workflow")
    assert circle_ci_runs == []
    

def test_get_circle_ci_runs_not_found():
    pass

