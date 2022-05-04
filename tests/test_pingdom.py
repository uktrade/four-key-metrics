import os

import httpretty
import pytest

from four_key_metrics.gateways import PingdomErrors
from four_key_metrics.domain_models import PingdomError

from tests.mock_pingdom_request import httpretty_checks
from tests.mock_pingdom_request import httpretty_analysis_p1
from tests.mock_pingdom_request import httpretty_analysis_p1_1226770577
from tests.mock_pingdom_request import httpretty_analysis_p1_1226773180
from tests.mock_pingdom_request import httpretty_analysis_p1_1233552532


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


@pytest.mark.parametrize(
    "pingdom_check_id, expected_result",
    [
        (
            4946807,
            [
                {
                    "id": 1226774223,
                    "timefirsttest": 1649109749,
                    "timeconfirmtest": 1649109750,
                },
                {
                    "id": 1226773180,
                    "timefirsttest": 1649109569,
                    "timeconfirmtest": 1649109572,
                },
                {
                    "id": 1226770577,
                    "timefirsttest": 1649108669,
                    "timeconfirmtest": 1649108672,
                },
            ],
        ),
    ],
)
def test_get_analysis_for_pingdom_id(pingdom_check_id, expected_result, pingdom_errors):
    httpretty_checks()
    httpretty_analysis_p1()

    pingdom_info = pingdom_errors._get_pingdom_analysis(pingdom_check_id)

    assert pingdom_info == expected_result


@pytest.mark.parametrize(
    "pingdom_check_id, analysis_id, expected_result",
    [
        # (4946807, 1226770577),
        (
            4946807,
            1226773180,
            (
                "1649109575",
                "1649109578",
            ),
        ),
    ],
)
def test_get_analysis_details_for_pingdom_id_and_analysis_id(
    pingdom_check_id, analysis_id, expected_result, pingdom_errors
):
    httpretty_checks()
    httpretty_analysis_p1()
    httpretty_analysis_p1_1226770577()
    httpretty_analysis_p1_1226773180()
    httpretty_analysis_p1_1233552532()

    pingdom_info = pingdom_errors._get_pingdom_analysis_details(
        pingdom_check_id, analysis_id
    )

    assert pingdom_info == expected_result


def test_get_pingdom_errors(pingdom_errors):

    httpretty_checks()
    httpretty_analysis_p1()
    httpretty_analysis_p1_1226770577()
    httpretty_analysis_p1_1226773180()
    httpretty_analysis_p1_1233552532()

    pingdom_check_names = [
        "Data Hub P1",
    ]
    expected_result = [
        PingdomError(
            check_name="Data Hub P1",
            check_id=4946807,
            error_id=1226774223,
            down_timestamp="1649109752",
            up_timestamp="1649109754",
        ),
        PingdomError(
            check_name="Data Hub P1",
            check_id=4946807,
            error_id=1226773180,
            down_timestamp="1649109575",
            up_timestamp="1649109578",
        ),
        PingdomError(
            check_name="Data Hub P1",
            check_id=4946807,
            error_id=1226770577,
            down_timestamp="1649108675",
            up_timestamp="1649108677",
        ),
    ]
    assert (
        pingdom_errors.get_pingdom_errors(pingdom_check_names)[0].__dict__
        == expected_result[0].__dict__
    )
