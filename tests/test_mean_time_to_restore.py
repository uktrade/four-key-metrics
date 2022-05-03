import os

import httpretty
import pytest

from four_key_metrics.mean_time_to_restore_metrics import get_pingdom_id_for_check_names

from tests.mock_pingdom_request import httpretty_checks


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_get_pingdom_id_for_check_names(capsys):
    httpretty_checks()
    pingdom_check_names = [
        "uk.gov.trade.datahub.api",
        "Data Hub P1",
        "Data Hub P2",
    ]

    pingdom_info = get_pingdom_id_for_check_names(pingdom_check_names)

    assert pingdom_info["uk.gov.trade.datahub.api"] == 3966721
    assert pingdom_info["Data Hub P2"] == 5654644
    assert pingdom_info["Data Hub P1"] == 4946807
