import csv
import httpretty
import os
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


def generate_mean_time_to_restore_to_csv():
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, CSVDataPresenter.create()
    )


def clean_up_csv_file(csv_filename):
    file_exists = os.path.exists(csv_filename)
    if file_exists:
        os.remove(csv_filename)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["PINGDOM_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


def test_csv_created(capsys):
    generate_mean_time_to_restore_to_csv()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)
    file_exists = os.path.exists(csv_filename)
    assert "CSV metrics stored in mean_time_to_restore_" in captured.out
    assert file_exists
    clean_up_csv_file(csv_filename)


def test_mean_time_to_restore_csv(capsys):
    generate_mean_time_to_restore_to_csv()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)

    with open(csv_filename, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)

        assert csvreader.fieldnames.__contains__("source")
        assert csvreader.fieldnames.__contains__("project")
        assert csvreader.fieldnames.__contains__("down_timestamp")
        assert csvreader.fieldnames.__contains__("down_time")
        assert csvreader.fieldnames.__contains__("up_timestamp")
        assert csvreader.fieldnames.__contains__("up_time")
        assert csvreader.fieldnames.__contains__("seconds_to_restore")
    clean_up_csv_file(csv_filename)
