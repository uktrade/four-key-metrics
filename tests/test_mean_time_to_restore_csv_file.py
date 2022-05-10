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


def test_mean_time_to_restore_csv_headers(capsys):
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


def test_mean_time_to_restore_csv_content(capsys):
    generate_mean_time_to_restore_to_csv()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)

    with open(csv_filename, newline="") as csvfile:
        csvreader_list = list(csv.DictReader(csvfile))

        assert csvreader_list[0]["source"] == "pingdom"
        assert csvreader_list[0]["project"] == "Data Hub P1"
        assert csvreader_list[0]["down_timestamp"] == "1637168609"
        assert csvreader_list[0]["down_time"] == "17/11/2021 17:03:29"
        assert csvreader_list[0]["up_timestamp"] == "1637172329"
        assert csvreader_list[0]["up_time"] == "17/11/2021 18:05:29"
        assert csvreader_list[0]["seconds_to_restore"] == "3720"

        assert csvreader_list[1]["source"] == "pingdom"
        assert csvreader_list[1]["project"] == "Data Hub P1"
        assert csvreader_list[1]["down_timestamp"] == "1641082949"
        assert csvreader_list[1]["down_time"] == "02/01/2022 00:22:29"
        assert csvreader_list[1]["up_timestamp"] == "1641083189"
        assert csvreader_list[1]["up_time"] == "02/01/2022 00:26:29"
        assert csvreader_list[1]["seconds_to_restore"] == "240"
