import os

import httpretty
import pytest

from four_key_metrics.domain_models import Build
from four_key_metrics.gateways import JenkinsBuilds
from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)
from four_key_metrics.presenters.mean_time_to_restore import (
    ConsolePresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_jenkins_request import (
    httpretty_four_jenkins_builds_two_failures,
    httpretty_two_jenkins_builds_failures_in_row,
    httpretty_four_jenkins_builds_two_failures_mixed_envs,
)
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
    os.environ["DIT_JENKINS_USER"] = "test"
    os.environ["DIT_JENKINS_TOKEN"] = "1234"
    os.environ["DIT_JENKINS_URI"] = "https://jenkins.test/"
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


def test_get_jenkins_outages():
    httpretty_four_jenkins_builds_two_failures()

    outages = JenkinsBuilds("https://jenkins.test/").get_jenkins_outages(["test-job"])
    assert len(outages) == 2

    for o in outages:
        assert o.source == "jenkins"
        assert o.environment == "production"
        assert o.project == "test-job"

    assert outages[0].seconds_to_restore == 2511671.0
    assert outages[1].seconds_to_restore == 1210.0
    assert outages[0].jenkins_failed_build_hash == "build-sha-1"
    assert outages[1].jenkins_failed_build_hash == "build-sha-4"


def test_group_builds_by_environment():
    failing_dev_build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:40:45Z",
        successful=False,
        environment="development",
        git_reference="sha1-git-reference",
    )
    successful_dev_build = Build(
        started_at="2021-09-17T13:35:45Z",
        finished_at="2021-09-17T13:37:45Z",
        successful=True,
        environment="development",
        git_reference="sha1-git-reference",
    )
    failing_staging_build = Build(
        started_at="2021-09-17T13:30:45Z",
        finished_at="2021-09-17T13:30:45Z",
        successful=False,
        environment="staging",
        git_reference="sha1-git-reference",
    )

    builds = [
        failing_dev_build,
        successful_dev_build,
        failing_staging_build,
    ]

    grouped_builds = JenkinsBuilds("https://jenkins.test/").group_builds_by_environment(
        builds
    )
    assert grouped_builds == {
        "development": [failing_dev_build, successful_dev_build],
        "staging": [failing_staging_build],
    }


def test_get_jenkins_outages_with_builds_from_different_environments():
    httpretty_four_jenkins_builds_two_failures_mixed_envs()
    outages = JenkinsBuilds("https://jenkins.test/").get_jenkins_outages(["test-job"])
    assert len(outages) == 2

    development_outage = next(
        (o for o in outages if o.environment == "development"), None
    )
    staging_outage = next((o for o in outages if o.environment == "staging"), None)

    assert development_outage.seconds_to_restore == 640
    assert staging_outage.seconds_to_restore == 642


def xtest_what_happens_if_the_latest_build_fails_and_there_is_no_success(capsys):
    pass


def test_two_failed_builds_in_a_row():
    httpretty_two_jenkins_builds_failures_in_row()

    outages = JenkinsBuilds("https://jenkins.test/").get_jenkins_outages(["test-job"])
    assert len(outages) == 1
    assert outages[0].seconds_to_restore == 5280142
