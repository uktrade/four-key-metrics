import os

import httpretty
import pytest

from four_key_metrics.gateways import JenkinsBuilds
from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)
from four_key_metrics.presenters.mean_time_to_restore import (
    ConsolePresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory
from tests.mock_jenkins_request import httpretty_four_jenkins_builds_two_failures
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


def xtest_mean_time_to_restore_jenkins(capsys):
    httpretty_four_jenkins_builds_two_failures()
    ## Mock data for reference
    # 1st FAILURE: 1643768542000
    # 1st SUCCESS: 1646278413000

    # 2nd FAILURE: 1649047474000
    # 2nd SUCCESS: 1649047484000
    outages = GenerateMeanTimeToRestore()._get_jenkins_mean_time_to_restore("test-job")
    assert len(outages) == 2

    for o in outages:
        assert o.source == "jenkins"
        # assert o.project - how do we get the project is that the job that's passed in?

    # assert down_timestamp (failure build timestamp)
    # assert up_timestamp (next success build timestamp)
    # assert environment in outage object (need to add to Outage class)
    # assert check_id is the build commit hash (need to change name of check_id in Outage class)
    assert outages[0].seconds_to_restore == 2509871000
    assert outages[1].seconds_to_restore == 10000
