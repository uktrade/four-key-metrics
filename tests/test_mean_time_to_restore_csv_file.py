import csv
import os

import httpretty
import pytest

from four_key_metrics.presenters.mean_time_to_restore import (
    CSVDataPresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_jenkins_request import httpretty_four_jenkins_builds_two_failures
from tests.mock_pingdom_request import httpretty_checks, httpretty_summary_outage_p1
from tests.utilities import clean_up_test_file, get_filename_and_captured_outerr


def get_csv_filename_and_captured_outerr(capsys):
    return get_filename_and_captured_outerr(capsys, "mean_time_to_restore_", "csv")


def generate_mean_time_to_restore_to_csv():
    httpretty_checks()
    httpretty_summary_outage_p1()
    httpretty_four_jenkins_builds_two_failures()
    check_names = ["Data Hub P1"]
    jenkins_jobs = ["test-job"]

    UseCaseFactory().create("generate_mean_time_to_restore")(
        check_names, jenkins_jobs, CSVDataPresenter.create()
    )


class TestMeanTimeToRestoreCSVFile:
    @pytest.fixture(autouse=True)
    def around_each(self, capsys):
        httpretty.enable(allow_net_connect=False, verbose=True)
        os.environ["PINGDOM_TOKEN"] = "1234"
        os.environ["DIT_JENKINS_USER"] = "test"
        os.environ["DIT_JENKINS_TOKEN"] = "1234"
        os.environ["DIT_JENKINS_URI"] = "https://jenkins.test/"
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
            assert csvreader.fieldnames.__contains__("environment")
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
            assert csvreader_list[0]["environment"] == "production"
            assert csvreader_list[0]["down_timestamp"] == "1637168609"
            assert csvreader_list[0]["down_time"] == "17/11/2021 17:03:29"
            assert csvreader_list[0]["up_timestamp"] == "1637172329"
            assert csvreader_list[0]["up_time"] == "17/11/2021 18:05:29"
            assert csvreader_list[0]["seconds_to_restore"] == "3720"

            assert csvreader_list[1]["source"] == "pingdom"
            assert csvreader_list[1]["project"] == "Data Hub P1"
            assert csvreader_list[1]["environment"] == "production"
            assert csvreader_list[1]["down_timestamp"] == "1641082949"
            assert csvreader_list[1]["down_time"] == "02/01/2022 00:22:29"
            assert csvreader_list[1]["up_timestamp"] == "1641083189"
            assert csvreader_list[1]["up_time"] == "02/01/2022 00:26:29"
            assert csvreader_list[1]["seconds_to_restore"] == "240"

            assert csvreader_list[2]["source"] == "jenkins"
            assert csvreader_list[2]["project"] == "test-job"
            assert csvreader_list[2]["environment"] == "production"
            assert csvreader_list[2]["down_timestamp"] == "1643768542"
            assert csvreader_list[2]["down_time"] == "02/02/2022 02:22:22"
            assert csvreader_list[2]["up_timestamp"] == "1646280213"
            assert csvreader_list[2]["up_time"] == "03/03/2022 04:03:33"
            assert csvreader_list[2]["seconds_to_restore"] == "2511671"

            assert csvreader_list[3]["source"] == "jenkins"
            assert csvreader_list[3]["project"] == "test-job"
            assert csvreader_list[3]["environment"] == "production"
            assert csvreader_list[3]["down_timestamp"] == "1649047474"
            assert csvreader_list[3]["down_time"] == "04/04/2022 05:44:34"
            assert csvreader_list[3]["up_timestamp"] == "1649048684"
            assert csvreader_list[3]["up_time"] == "04/04/2022 06:04:44"
            assert csvreader_list[3]["seconds_to_restore"] == "1210"
