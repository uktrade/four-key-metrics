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


@pytest.mark.parametrize(
    "pingdom_check_names,expected_result,expected_terminal_output",
    [
        (
            [
                "uk.gov.trade.datahub.api",
                "Data Hub P1",
                "Data Hub P2",
            ],
            {
                "uk.gov.trade.datahub.api": 3966721,
                "Data Hub P1": 4946807,
                "Data Hub P2": 5654644,
            },
            "",
        ),
        (
            [
                "uk.gov.trade.datahub.api",
                "Can't find me",
                "Data Hub P2",
            ],
            {
                "uk.gov.trade.datahub.api": 3966721,
                "Data Hub P2": 5654644,
            },
            "WARNING: Not all Pingdom checks found. Check for typos.",
        ),
    ],
)
def test_get_pingdom_id_for_check_names(
    capsys, pingdom_check_names, expected_result, expected_terminal_output
):
    httpretty_checks()
    pingdom_info = get_pingdom_id_for_check_names(pingdom_check_names)

    captured = capsys.readouterr()

    assert pingdom_info == expected_result
    assert expected_terminal_output in captured.out
