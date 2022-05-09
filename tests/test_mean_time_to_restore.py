import os

import httpretty
import pytest

from four_key_metrics.use_case.generate_mean_time_to_restore import (
    get_pingdom_mean_time_to_restore,
)
from four_key_metrics.gateways import PingdomErrors
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_get_pingdom_mean_time_to_restore():
    httpretty_checks()
    httpretty_summary_outage_p1()
    assert get_pingdom_mean_time_to_restore(["Data Hub P1"]) == 1980.0
