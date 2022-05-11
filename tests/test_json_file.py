import json
import os
import re

import httpretty
import pytest

from four_key_metrics.file_utilities import remove_generated_reports
from four_key_metrics.presenters.lead_time_metrics import JSONDataPresenter
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_github_request import httpretty_two_github_requests
from tests.mock_jenkins_request import httpretty_two_jenkins_builds
from tests.utilities import get_filename_and_captured_outerr


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["DIT_JENKINS_USER"] = "test"
    os.environ["DIT_JENKINS_TOKEN"] = "1234"
    os.environ["DIT_JENKINS_URI"] = "https://jenkins.test/"
    os.environ["GITHUB_USERNAME"] = "git_test"
    os.environ["GITHUB_TOKEN"] = "1234"
    os.environ["EXCLUDED_DEPLOYMENT_HASHES"] = '["1234"]'
    httpretty.reset()
    yield
    httpretty.disable()
    remove_generated_reports(".json")


def get_json_filename_and_captured_outerr(capsys):
    return get_filename_and_captured_outerr(capsys, "lead_time_metrics_", "json")


def run_display_with_simple_builds():
    httpretty_two_jenkins_builds()
    httpretty_two_github_requests()
    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        }
    ]

    UseCaseFactory().create("generate_lead_time_metrics")(
        projects, JSONDataPresenter()
    )


def test_json_is_created_and_then_successfully_removed(capsys):
    run_display_with_simple_builds()
    json_filename, captured = get_json_filename_and_captured_outerr(capsys)
    file_exists = os.path.exists(json_filename)
    assert "JSON metrics stored in lead_time_metrics_" in captured.out
    assert file_exists
    if file_exists:
        remove_generated_reports(".json")
        assert os.path.exists(json_filename) is False


def test_csv_github_commits(capsys):
    run_display_with_simple_builds()
    json_filename, captured = get_json_filename_and_captured_outerr(capsys)

    with open(json_filename) as json_file:
        actual_data = json.load(json_file)
        assert actual_data[0]["repository"] == "test-repository"
        assert actual_data[0]["build_commit_hash"] == "build-sha-2"
        assert actual_data[0]["build_time"] == "03/03/2022 03:43:33"
        assert actual_data[0]["build_timestamp"] == 1646279013.0
        assert actual_data[0]["commit_hash"] == "commit-sha1"
        assert actual_data[0]["commit_lead_time"] == "61 days, 2:42:32"
        assert actual_data[0]["commit_lead_time_days"] == 61.11287037037037
        assert actual_data[0]["commit_time"] == "01/01/2022 01:01:01"
        assert actual_data[0]["commit_timestamp"] == 1640998861.0
        assert actual_data[0]["previous_build_commit_hash"] == "build-sha-1"

        assert actual_data[1]["repository"] == "test-repository"
        assert actual_data[1]["build_commit_hash"] == "build-sha-2"
        assert actual_data[1]["build_time"] == "03/03/2022 03:43:33"
        assert actual_data[1]["build_timestamp"] == 1646279013.0
        assert actual_data[1]["commit_hash"] == "commit-sha2"
        assert actual_data[1]["commit_lead_time"] == "60 days, 1:41:31"
        assert actual_data[1]["commit_lead_time_days"] == 60.07049768518519
        assert actual_data[1]["commit_time"] == "02/01/2022 02:02:02"
        assert actual_data[1]["commit_timestamp"] == 1641088922.0
        assert actual_data[1]["previous_build_commit_hash"] == "build-sha-1"
