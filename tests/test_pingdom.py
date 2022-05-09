import os

import httpretty
import pytest

from four_key_metrics.gateways import PingdomErrors
from four_key_metrics.domain_models import PingdomError

from tests.mock_pingdom_request import (
    httpretty_checks,
    httpretty_summary_outage_p1,
    httpretty_summary_outage_blank,
)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


@pytest.fixture()
def pingdom_errors():
    return PingdomErrors()


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
    capsys,
    pingdom_check_names,
    expected_result,
    expected_terminal_output,
    pingdom_errors,
):
    httpretty_checks()
    pingdom_info = pingdom_errors._get_pingdom_id_for_check_names(pingdom_check_names)

    captured = capsys.readouterr()

    assert pingdom_info == expected_result
    assert expected_terminal_output in captured.out


@pytest.mark.freeze_time("2022-05-09")
@pytest.mark.parametrize(
    "pingdom_check_id, from_timestamp_arg, expected_from_timestamp, expected_result",
    [
        (
            4946807,
            None,
            1636502400,
            [
                {"down_timestamp": 1637168609, "up_timestamp": 1637172329},
                {"down_timestamp": 1641082949, "up_timestamp": 1641083189},
            ],
        ),
        (
            4946807,
            1620571206,
            1620571206,
            [
                {"down_timestamp": 1637168609, "up_timestamp": 1637172329},
                {"down_timestamp": 1641082949, "up_timestamp": 1641083189},
            ],
        ),
    ],
)
def test_get_summary_outage_for_check_id(
    pingdom_check_id,
    from_timestamp_arg,
    expected_from_timestamp,
    expected_result,
    pingdom_errors,
):
    httpretty_checks()
    httpretty_summary_outage_p1()

    pingdom_info = pingdom_errors._get_pingdom_outage_summary(
        pingdom_check_id, from_timestamp_arg
    )

    assert pingdom_info == expected_result
    assert (
        httpretty.last_request().url
        == f"https://api.pingdom.com/api/3.1/summary.outage/4946807?from={expected_from_timestamp}"
    )


def test_get_summary_outage_no_outages(pingdom_errors):
    httpretty_checks()
    httpretty_summary_outage_blank()

    pingdom_info = pingdom_errors._get_pingdom_outage_summary(4946807)
    assert pingdom_info == []


def test_get_pingdom_errors(pingdom_errors):

    httpretty_checks()
    httpretty_summary_outage_p1()

    pingdom_check_names = [
        "Data Hub P1",
    ]

    expected_result = [
        PingdomError(
            check_name="Data Hub P1",
            check_id=4946807,
            down_timestamp=1637168609,
            up_timestamp=1637172329,
        ),
        PingdomError(
            check_name="Data Hub P1",
            check_id=4946807,
            down_timestamp=1641082949,
            up_timestamp=1641083189,
        ),
    ]
    assert (
        pingdom_errors.get_pingdom_errors(pingdom_check_names)[0].__dict__
        == expected_result[0].__dict__
    )
