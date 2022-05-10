import os

import httpretty
import pytest

from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)
from four_key_metrics.presenters.mean_time_to_restore import ConsolePresenter
from four_key_metrics.use_case_factory import UseCaseFactory

from four_key_metrics.gateways import PingdomErrors
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1
from display import DisplayShell


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

    generate_mean_time_to_restore = GenerateMeanTimeToRestore()
    assert (
        generate_mean_time_to_restore._get_pingdom_mean_time_to_restore(["Data Hub P1"])
        == 1980
    )


def xtest_mean_time_to_restore_output():
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, ConsoleOnlyPresenter()
    )

    expect_result = {
        "source": "pingdom",
        "project": "Data Hub P1",
        "average": 1980,
    }

    captured = capsys.readouterr()
    assert expect_result in captured.out


def xtest_do_mean_time_to_restore():
    display_shell = DisplayShell()
    display_shell.do_mean_time_to_restore(["Data Hub P1"])

    assert false
