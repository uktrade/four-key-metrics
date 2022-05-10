import os
import httpretty
import pytest

from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)
from four_key_metrics.presenters.mean_time_to_restore import (
    ConsolePresenter,
    CSVDataPresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from four_key_metrics.gateways import PingdomOutages
from tests.utilities import get_filename_and_captured_outerr
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1


def get_csv_filename_and_captured_outerr(capsys):
    return get_filename_and_captured_outerr(capsys, "mean_time_to_restore_", "csv")


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_csv_created(capsys):
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, CSVDataPresenter.create()
    )

    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)
    file_exists = os.path.exists(csv_filename)
    assert "CSV metrics stored in mean_time_to_restore_" in captured.out
    assert file_exists
    if file_exists:
        os.remove(csv_filename)
        assert os.path.exists(csv_filename) is False


def test_mean_time_to_restore_csv(capsys):
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, CSVDataPresenter.create()
    )

    # Check
    captured = capsys.readouterr()
    assert "'source': 'pingdom'" in captured.out
    assert "'average': 1980" in captured.out
    assert "'count': 2" in captured.out
