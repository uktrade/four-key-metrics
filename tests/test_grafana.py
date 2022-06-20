import os

import httpretty
import pytest
from freezegun import freeze_time

from four_key_metrics.domain_models import Outage
from four_key_metrics.gateways.grafana import GrafanaAlertAnnotation
from tests.mock_grafana_request import (
    httpretty_grafana_alerts,
    httpretty_grafana_alert_annotations,
    httpretty_no_grafana_alerts,
    httpretty_404_grafana_alerts,
    httpretty_503_grafana_alerts,
    httpretty_no_grafana_alert_annotations,
    httpretty_404_grafana_alert_annotations,
    httpretty_503_grafana_alert_annotations,
)


@pytest.fixture(autouse=True)
def around_each():
    httpretty.enable(allow_net_connect=False, verbose=True)
    os.environ["GRAFANA_TOKEN"] = "1234"
    httpretty.reset()
    yield
    httpretty.disable()


@pytest.fixture()
def grafana_alert_annotation():
    return GrafanaAlertAnnotation()


def test_empty_grafana_alerts(capsys, grafana_alert_annotation):
    httpretty_404_grafana_alerts()

    grafana_outages = grafana_alert_annotation._get_alert_uids_from_names([])

    captured = capsys.readouterr()
    assert "Not Found [404] whilst loading " in captured.out
    assert "Check your project's job name." in captured.out


def test_no_grafana_alerts(capsys, grafana_alert_annotation):
    httpretty_no_grafana_alerts()

    alert_uids = grafana_alert_annotation._get_alert_uids_from_names([])

    assert len(alert_uids) == 0


def test_404_grafana_alerts(capsys, grafana_alert_annotation):
    httpretty_404_grafana_alerts()

    grafana_outages = grafana_alert_annotation._get_alert_uids_from_names(["not-here"])

    captured = capsys.readouterr()
    assert "Not Found [404] whilst loading " in captured.out
    assert "Check your project's job name." in captured.out


def test_503_grafana_alerts(capsys, grafana_alert_annotation):
    httpretty_503_grafana_alerts()

    grafana_outages = grafana_alert_annotation._get_alert_uids_from_names(["not-here"])

    captured = capsys.readouterr()
    # assert all_builds
    assert "Service Unavailable [503] whilst loading " in captured.out
    assert "Check your project's job name." not in captured.out


def test_no_grafana_alert_notifications(grafana_alert_annotation):
    httpretty_grafana_alerts()
    httpretty_no_grafana_alert_annotations()

    all_outages = GrafanaAlertAnnotation().get_grafana_outages(
        [{"name": "Test Grafana Alert", "environment": "testing"}]
    )

    assert len(all_outages) == 0


def test_not_all_grafana_alert_names(capsys, grafana_alert_annotation):
    httpretty_grafana_alerts()
    httpretty_no_grafana_alert_annotations()

    #    grafana_outages = grafana_alert_annotation._get_alert_uids_from_names(["Test Grafana Alert"])
    all_outages = GrafanaAlertAnnotation().get_grafana_outages(
        [
            {"name": "Test Grafana Alert", "environment": "testing"},
            {"name": "Not here", "environment": "failing"},
        ]
    )

    captured = capsys.readouterr()
    assert (
        "WARNING: Not all Grafana alert names found. Check for typos." in captured.out
    )


def test_404_grafana_alert_notifications(capsys, grafana_alert_annotation):
    httpretty_grafana_alerts()
    httpretty_404_grafana_alert_annotations()

    all_outages = GrafanaAlertAnnotation().get_grafana_outages(
        [{"name": "Test Grafana Alert", "environment": "testing"}]
    )

    captured = capsys.readouterr()
    assert "Not Found [404] whilst loading " in captured.out
    assert "Check your grafana alert id." in captured.out


def test_503_grafana_alert_notifications(capsys, grafana_alert_annotation):
    httpretty_grafana_alerts()
    httpretty_503_grafana_alert_annotations()

    all_outages = GrafanaAlertAnnotation().get_grafana_outages(
        [{"name": "Test Grafana Alert", "environment": "testing"}]
    )

    captured = capsys.readouterr()
    assert "Service Unavailable [503] whilst loading " in captured.out
    assert "Check your grafana alert id." not in captured.out


def test_grafana_alert_annotations_from_timestamp(grafana_alert_annotation):
    httpretty_grafana_alerts()
    httpretty_grafana_alert_annotations()

    grafana_outages = grafana_alert_annotation._get_grafana_alert_annotations(
        1, 1655113230101
    )

    assert (
        httpretty.last_request().url == f"https://grafana.ci.uktrade.digital/"
        "api/annotations?alertId=1&from=1655113230101"
    )


def xtest_get_pingdom_no_checks(pingdom_outages):
    httpretty_no_checks()
    httpretty_summary_outage_blank()

    pingdom_info = pingdom_outages._get_pingdom_id_for_check_names([])

    assert pingdom_info == {}


def xtest_get_summary_outage_no_outages(capsys, pingdom_outages):
    httpretty_checks()
    httpretty_summary_outage_status(404)

    pingdom_info = pingdom_outages._get_pingdom_outage_summary(4946807)

    captured = capsys.readouterr()
    # assert all_builds
    assert "Not Found [404] whilst loading " in captured.out
    assert "Check your pingdom check id." in captured.out
    assert pingdom_info == {}


def xtest_get_summary_outage_503_outages(capsys, pingdom_outages):
    httpretty_checks()
    httpretty_summary_outage_status(503)

    pingdom_info = pingdom_outages._get_pingdom_outage_summary(4946807)

    captured = capsys.readouterr()
    # assert all_builds
    assert "Service Unavailable [503] whilst loading " in captured.out
    assert "Check your pingdom check id." not in captured.out
    assert pingdom_info == {}


def xtest_get_summary_outage_no_outage_summary(pingdom_outages):
    httpretty_checks()
    httpretty_summary_outage_blank()

    pingdom_info = pingdom_outages._get_pingdom_outage_summary(4946807)
    assert pingdom_info == []


def xtest_get_pingdom_outages(pingdom_outages):

    httpretty_checks()
    httpretty_summary_outage_p1()

    pingdom_check_names = [
        "Data Hub P1",
    ]

    expected_result = [
        Outage(
            source="pingdom",
            environment="production",
            project="Data Hub P1",
            pingdom_check_id=4946807,
            down_timestamp=1637168609,
            up_timestamp=1637172329,
        ),
        Outage(
            source="pingdom",
            environment="production",
            project="Data Hub P1",
            pingdom_check_id=4946807,
            down_timestamp=1641082949,
            up_timestamp=1641083189,
        ),
    ]
    assert (
        pingdom_outages.get_pingdom_outages(pingdom_check_names)[0].__dict__
        == expected_result[0].__dict__
    )


def xtest_calculate_time_to_restore():
    pingdomOutage = Outage(
        source="pingdom",
        environment="production",
        project="Test check",
        pingdom_check_id=123,
        down_timestamp=1652114557,
        up_timestamp=1652114577,
    )
    assert pingdomOutage.seconds_to_restore == 20
