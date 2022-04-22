import csv
import httpretty
import os
import re
import pprint
import pytest

from four_key_metrics.lead_time_metrics import generate_lead_time_metrics

from tests.mock_jenkins_request import httpretty_two_jenkins_builds
from tests.mock_github_request import httpretty_two_github_requests


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


def get_csv_filename_and_captured_outerr(capsys):
    captured = capsys.readouterr()
    # Extract filename from output
    regex_filename = r"lead_time_metrics_[0-9]{2}-[0-9]{2}-[0-9]{4}_[0-9]{6}.csv"
    csv_filename = re.search(regex_filename, captured.out).group()
    return csv_filename, captured


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

    generate_lead_time_metrics(projects)


def test_csv_created(capsys):
    run_display_with_simple_builds()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)
    assert "Detailed metrics stored in lead_time_metrics_" in captured.out
    assert os.path.exists(csv_filename)


def test_column_names_in_csv_file(capsys):
    run_display_with_simple_builds()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)

    with open(csv_filename, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)

        assert csvreader.fieldnames.__contains__("repository")
        assert csvreader.fieldnames.__contains__("build_commit_hash")
        assert csvreader.fieldnames.__contains__("build_timestamp")
        assert csvreader.fieldnames.__contains__("build_time")
        assert csvreader.fieldnames.__contains__("commit_hash")
        assert csvreader.fieldnames.__contains__("commit_timestamp")
        assert csvreader.fieldnames.__contains__("commit_time")
        assert csvreader.fieldnames.__contains__("commit_lead_time_days")
        assert csvreader.fieldnames.__contains__("commit_lead_time")
        assert csvreader.fieldnames.__contains__("previous_build_commit_hash")


def test_csv_github_commits(capsys):
    run_display_with_simple_builds()
    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)

    with open(csv_filename, newline="") as csvfile:
        csvreader_list = list(csv.DictReader(csvfile))

        assert csvreader_list[0]["repository"] == "test-repository"
        assert csvreader_list[0]["build_commit_hash"] == "build-sha-2"
        assert csvreader_list[0]["build_time"] == "03/03/2022 03:43:33"
        assert csvreader_list[0]["build_timestamp"] == "1646279013.0"
        assert csvreader_list[0]["commit_hash"] == "commit-sha1"
        assert csvreader_list[0]["commit_lead_time"] == "61 days, 2:42:32"
        assert csvreader_list[0]["commit_lead_time_days"] == "61.11287037037037"
        assert csvreader_list[0]["commit_time"] == "01/01/2022 01:01:01"
        assert csvreader_list[0]["commit_timestamp"] == "1640998861.0"
        assert csvreader_list[0]["previous_build_commit_hash"] == "build-sha-1"

        assert csvreader_list[1]["repository"] == "test-repository"
        assert csvreader_list[1]["build_commit_hash"] == "build-sha-2"
        assert csvreader_list[1]["build_time"] == "03/03/2022 03:43:33"
        assert csvreader_list[1]["build_timestamp"] == "1646279013.0"
        assert csvreader_list[1]["commit_hash"] == "commit-sha2"
        assert csvreader_list[1]["commit_lead_time"] == "60 days, 1:41:31"
        assert csvreader_list[1]["commit_lead_time_days"] == "60.07049768518519"
        assert csvreader_list[1]["commit_time"] == "02/01/2022 02:02:02"
        assert csvreader_list[1]["commit_timestamp"] == "1641088922.0"
        assert csvreader_list[1]["previous_build_commit_hash"] == "build-sha-1"


def test_multiple_projects(capsys):
    httpretty_two_jenkins_builds()
    httpretty_two_github_requests()
    httpretty_two_github_requests(
        "build-sha-1", "build-sha-2", "test-repository-another"
    )
    projects = [
        {
            "job": "test-job",
            "repository": "test-repository",
            "environment": "production",
        },
        {
            "job": "test-job",
            "repository": "test-repository-another",
            "environment": "production",
        },
    ]
    generate_lead_time_metrics(projects)

    csv_filename, captured = get_csv_filename_and_captured_outerr(capsys)

    fileoutput = []
    with open(csv_filename, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)

        # Count occurances of repositories (should be two each)
        test_repository_count = 0
        test_repository_another_count = 0
        fileoutput = []
        for row in csvreader:
            fileoutput.append(pprint.pformat(row["repository"]))
            if row["repository"] == "test-repository":
                test_repository_count += 1
            if row["repository"] == "test-repository-another":
                test_repository_another_count += 1

        assert test_repository_count == 2
        assert test_repository_another_count == 2
