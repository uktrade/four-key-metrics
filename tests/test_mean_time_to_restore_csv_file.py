import csv
import os

import httpretty
import pytest

from four_key_metrics.presenters.mean_time_to_restore import (
    CSVDataPresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1
from tests.utilities import clean_up_test_file, get_filename_and_captured_outerr


def get_csv_filename_and_captured_outerr(capsys):
    return get_filename_and_captured_outerr(capsys, "mean_time_to_restore_", "csv")


def generate_mean_time_to_restore_to_csv():
    httpretty_checks()
    httpretty_summary_outage_p1()
    check_names = ["Data Hub P1"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, CSVDataPresenter.create()
    )


class TestMeanTimeToRestoreCSVFile:
    @pytest.fixture(autouse=True)
    def around_each(self, capsys):
        httpretty.enable(allow_net_connect=False, verbose=True)
        os.environ["PINGDOM_TOKEN"] = "1234"
        httpretty.reset()
        generate_mean_time_to_restore_to_csv()
        self.filename, self.captured = get_csv_filename_and_captured_outerr(capsys)
        yield
        clean_up_test_file(self.filename)
        httpretty.disable()

    def test_csv_created(self):
        file_exists = os.path.exists(self.filename)
        assert "CSV metrics stored in mean_time_to_restore_" in self.captured.out
        assert file_exists

    def test_mean_time_to_restore_csv_headers(self):
        with open(self.filename, newline="") as csvfile:
            csvreader = csv.DictReader(csvfile)

            assert csvreader.fieldnames.__contains__("source")
            assert csvreader.fieldnames.__contains__("project")
            assert csvreader.fieldnames.__contains__("down_timestamp")
            assert csvreader.fieldnames.__contains__("down_time")
            assert csvreader.fieldnames.__contains__("up_timestamp")
            assert csvreader.fieldnames.__contains__("up_time")
            assert csvreader.fieldnames.__contains__("seconds_to_restore")

    def test_mean_time_to_restore_csv_content(self):
        with open(self.filename, newline="") as csvfile:
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
