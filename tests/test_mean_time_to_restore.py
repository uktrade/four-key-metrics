import os

import httpretty
import pytest

from four_key_metrics.presenters.mean_time_to_restore import (
    ConsolePresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1


class ConsoleOnlyPresenter(ConsolePresenter):
    def add(self, data: dict):
        pass

    def begin(self):
        pass

    def end(self):
        pass


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_mean_time_to_restore_output_failure_pingdom(capsys):
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Failing"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    assert "'source': 'pingdom'" in captured.out
    assert "'mean time to restore in seconds': None" in captured.out
    assert "'count': None" in captured.out


def test_mean_time_to_restore_output_pingdom(capsys):
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, ConsoleOnlyPresenter()
    )

    captured = capsys.readouterr()
    assert "'source': 'pingdom'" in captured.out
    assert "'mean time to restore in seconds': 1980" in captured.out
    assert "'count': 2" in captured.out
