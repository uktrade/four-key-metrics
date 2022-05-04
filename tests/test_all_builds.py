import os

import httpretty
import pytest
import requests

from four_key_metrics.all_builds import AllBuilds

from tests.mock_jenkins_request import httpretty_404_no_job_jenkings_builds
from tests.mock_jenkins_request import httpretty_no_jenkings_builds
from tests.mock_jenkins_request import httpretty_one_jenkings_build
from tests.mock_jenkins_request import httpretty_two_jenkins_builds
from tests.mock_jenkins_request import (
    httpretty_two_jenkins_builds_one_production_one_development,
)

from tests.authorization_assertions import assert_authorization_is


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


def test_can_get_no_builds():
    all_builds = httpretty_no_jenkings_builds()
    builds = all_builds.get_jenkins_builds("test-job", "production")

    assert len(builds) == 0
    expected_url = (
        "https://jenkins.test/job/test-job/api/json"
        "?tree=allBuilds%5Btimestamp%2Cresult%2Cduration%2C"
        "actions%5Bparameters%5B%2A%5D%2C"
        "lastBuiltRevision%5Bbranch%5B%2A%5D%5D%5D%2C"
        "changeSet%5Bitems%5B%2A%5D%5D%5D"
    )

    assert expected_url == httpretty.last_request().url
    assert_authorization_is(b"test:1234")


def test_can_get_one_build():
    all_builds = httpretty_one_jenkings_build()
    builds = all_builds.get_jenkins_builds("test-job", "production")

    assert len(builds) == 1

    expected_url = (
        "https://jenkins.test/"
        "job/test-job/api/json"
        "?tree=allBuilds%5Btimestamp%2Cresult%2Cduration%2C"
        "actions%5Bparameters%5B%2A%5D%2ClastBuiltRevision"
        "%5Bbranch%5B%2A%5D%5D%5D%2C"
        "changeSet%5Bitems%5B%2A%5D%5D%5D"
    )
    assert expected_url == httpretty.last_request().url

    assert all_builds.builds[0].started_at == 1643768542.0
    assert all_builds.builds[0].finished_at == 1643769155.613
    assert all_builds.builds[0].successful
    assert all_builds.builds[0].environment == "production"
    assert all_builds.builds[0].git_reference == "1234"


def test_can_get_two_builds():
    all_builds = httpretty_two_jenkins_builds()
    builds = all_builds.get_jenkins_builds("test-job", "production")

    assert len(builds) == 2
    assert all_builds.builds[0].started_at == 1643768542.0
    assert all_builds.builds[0].finished_at == 1643769142.0
    assert not all_builds.builds[0].successful
    assert all_builds.builds[0].environment == "production"
    assert all_builds.builds[0].git_reference == "build-sha-1"

    assert all_builds.builds[1].started_at == 1646278413.0
    assert all_builds.builds[1].finished_at == 1646279013.0
    assert all_builds.builds[1].successful
    assert all_builds.builds[1].environment == "production"
    assert all_builds.builds[1].git_reference == "build-sha-2"


def test_can_get_environment_from_actions_list():
    actions = [
        {
            "_class": "hudson.model.ParametersAction",
            "parameters": [
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Environment",
                    "value": "production",
                },
                {
                    "_class": "hudson.model.StringParameterValue",
                    "name": "Git_Commit",
                    "value": "master",
                },
            ],
        },
        {
            "_class": "hudson.plugins.git.util.BuildData",
            "lastBuiltRevision": {
                "branch": [
                    {
                        "SHA1": "9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01",
                        "name": "origin/master",
                    }
                ]
            },
        },
    ]

    all_builds = AllBuilds("https://jenkins.ci.uktrade.digital/")

    sha1 = all_builds.get_action(
        "hudson.plugins.git.util.BuildData",
        ["lastBuiltRevision", "branch", 0, "SHA1"],
        actions,
    )
    assert "9cf68ec7e3c852ac0ff8da43fadbcbf27ac4eb01" == sha1

    environment = all_builds.get_action(
        "hudson.model.ParametersAction", ["parameters", 0, "value"], actions
    )
    assert "production" == environment


def test_add_project_fails_without_schema():
    all_builds = AllBuilds("")

    assert all_builds

    with pytest.raises(requests.exceptions.MissingSchema) as exception_info:
        all_builds.add_project("", "", "", "")
    assert "Invalid URL 'job//api/json': No scheme supplied. "
    "Perhaps you meant http://job//api/json?" in str(exception_info.value)


def test_no_jenkins_job(capsys):
    all_builds = httpretty_no_jenkings_builds()
    all_builds.get_jenkins_builds("test-job", "production")

    assert all_builds


def test_empty_add_project(capsys):
    httpretty_404_no_job_jenkings_builds()
    all_builds = httpretty_no_jenkings_builds()

    all_builds.get_jenkins_builds("test-job", "production")
    metrics = all_builds.add_project("", "", "", "")

    captured = capsys.readouterr()
    assert all_builds
    assert metrics["successful"] is False
    assert (
        "Not Found [404] whilst loading https://jenkins.test/job//api/json"
        "?tree=allBuilds%5Btimestamp%2Cresult%2Cduration%2Cactions"
        "%5Bparameters%5B%2A%5D%2ClastBuiltRevision%5Bbranch"
        "%5B%2A%5D%5D%5D%2CchangeSet%5Bitems%5B%2A%5D%5D%5D" in captured.out
    )
    assert "Check your project's job name." in captured.out
    assert metrics["lead_time_mean_average"] is None
    assert metrics["lead_time_standard_deviation"] is None


def test_can_get_no_lead_time():
    all_builds = httpretty_no_jenkings_builds()

    response = all_builds.add_project(
        jenkins_job="test-job",
        github_organisation="has-no-commits",
        github_repository="commit-less",
        environment="Production",
    )

    assert not response["successful"]
    assert response["lead_time_mean_average"] is None
    assert response["lead_time_standard_deviation"] is None


def test_can_not_get_lead_time_for_one_build():
    all_builds = httpretty_two_jenkins_builds()

    response = all_builds.add_project(
        jenkins_job="test-job",
        github_organisation="has-no-commits",
        github_repository="commit-less",
        environment="Production",
    )

    assert not response["successful"]
    assert response["lead_time_mean_average"] is None
    assert response["lead_time_standard_deviation"] is None


def test_can_not_get_lead_time_for_mismatched_environments():
    all_builds = httpretty_two_jenkins_builds_one_production_one_development()

    response = all_builds.add_project(
        jenkins_job="test-job",
        github_organisation="has-no-commits",
        github_repository="commit-less",
        environment="production",
    )

    assert not response["successful"]
    assert response["lead_time_mean_average"] is None
    assert response["lead_time_standard_deviation"] is None


def register_on_call_to_jenkins_a_connection_error_occurs():
    def a_connection_error_occurs(request, uri, headers):
        raise requests.exceptions.ConnectionError("Dummy Connection Error")

    httpretty.register_uri(
        httpretty.GET,
        "https://jenkins.test/" "job/test-job/api/json",
        status=200,
        body=a_connection_error_occurs,
    )


@pytest.mark.filterwarnings("ignore")
def test_can_tell_the_user_to_check_vpn_if_connection_issue(capsys):
    register_on_call_to_jenkins_a_connection_error_occurs()

    all_builds = AllBuilds("https://jenkins.test/")
    builds = all_builds.get_jenkins_builds("test-job", "production")
    captured = capsys.readouterr()

    assert len(builds) == 0
    assert "Are you connected to the VPN‽" in captured.out
