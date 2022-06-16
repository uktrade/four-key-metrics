import json

import httpretty


def httpretty_404_grafana_alerts():
    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/alerts",
        status=404,
    )
    return


def httpretty_503_grafana_alerts():
    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/alerts",
        status=503,
    )
    return


def httpretty_no_grafana_alerts():
    grafana = []

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/alerts",
        body=json.dumps(grafana),
    )
    return


def httpretty_grafana_alerts():
    grafana = [
        {
            "id": 1,
            "dashboardId": 11,
            "dashboardUid": "abcdef",
            "dashboardSlug": "test-grafana-alert",
            "panelId": 3,
            "name": "Test Grafana Alert",
            "state": "ok",
            "newStateDate": "2022-06-13T09:40:30Z",
            "evalDate": "0001-01-01T00:00:00Z",
            "evalData": {},
            "executionError": "",
            "url": "/d/abcdef/test-grafana-alert",
        }
    ]

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/alerts",
        body=json.dumps(grafana),
    )
    return


def httpretty_no_grafana_alert_annotations():
    grafana = []

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/annotations?alertId=1",
        body=json.dumps(grafana),
    )
    return


def httpretty_404_grafana_alert_annotations():
    grafana = []

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/annotations?alertId=1",
        status=404,
    )
    return


def httpretty_503_grafana_alert_annotations():
    grafana = []

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/annotations?alertId=1",
        status=503,
    )
    return


def httpretty_grafana_alert_annotations():
    grafana = [
        {
            "id": 80,
            "alertId": 1,
            "alertName": "Test Grafana Alert",
            "dashboardId": 11,
            "panelId": 3,
            "userId": 0,
            "newState": "ok",
            "prevState": "alerting",
            "created": 1655113230101,
            "updated": 1655113230101,
            "time": 1655113230100,
            "timeEnd": 1655113230100,
            "text": "",
            "tags": [],
            "login": "",
            "email": "",
            "avatarUrl": "",
            "data": {},
        },
        {
            "id": 79,
            "alertId": 1,
            "alertName": "Test Grafana Alert",
            "dashboardId": 11,
            "panelId": 3,
            "userId": 0,
            "newState": "alerting",
            "prevState": "pending",
            "created": 1655113110101,
            "updated": 1655113110101,
            "time": 1655113110101,
            "timeEnd": 1655113110101,
            "text": "",
            "tags": [],
            "login": "",
            "email": "",
            "avatarUrl": "",
            "data": {
                "evalMatches": [
                    {
                        "metric": 'connections{guid="5ead9f0d-b690-4eee-bda1-213eed567cd1", instance="metric-exporter.apps.internal:8080", job="govuk-paas-london", organisation="dit-services", service="datahub-db", source="sql", space="datahub"}',
                        "tags": {
                            "__name__": "connections",
                            "guid": "5ead9f0d-b690-4eee-bda1-213eed567cd1",
                            "instance": "metric-exporter.apps.internal:8080",
                            "job": "govuk-paas-london",
                            "organisation": "dit-services",
                            "service": "datahub-db",
                            "source": "sql",
                            "space": "datahub",
                        },
                        "value": 2,
                    }
                ]
            },
        },
        {
            "id": 78,
            "alertId": 1,
            "alertName": "Test Grafana Alert",
            "dashboardId": 11,
            "panelId": 3,
            "userId": 0,
            "newState": "pending",
            "prevState": "ok",
            "created": 1655113050101,
            "updated": 1655113050101,
            "time": 1655113050101,
            "timeEnd": 1655113050101,
            "text": "",
            "tags": [],
            "login": "",
            "email": "",
            "avatarUrl": "",
            "data": {
                "evalMatches": [
                    {
                        "metric": 'connections{guid="5ead9f0d-b690-4eee-bda1-213eed567cd1", instance="metric-exporter.apps.internal:8080", job="govuk-paas-london", organisation="dit-services", service="datahub-db", source="sql", space="datahub"}',
                        "tags": {
                            "__name__": "connections",
                            "guid": "5ead9f0d-b690-4eee-bda1-213eed567cd1",
                            "instance": "metric-exporter.apps.internal:8080",
                            "job": "govuk-paas-london",
                            "organisation": "dit-services",
                            "service": "datahub-db",
                            "source": "sql",
                            "space": "datahub",
                        },
                        "value": 4,
                    }
                ]
            },
        },
        {
            "id": 68,
            "alertId": 1,
            "alertName": "Test Grafana Alert",
            "dashboardId": 11,
            "panelId": 3,
            "userId": 0,
            "newState": "ok",
            "prevState": "alerting",
            "created": 1651051890266,
            "updated": 1651051890266,
            "time": 1651051890266,
            "timeEnd": 1651051890266,
            "text": "",
            "tags": [],
            "login": "",
            "email": "",
            "avatarUrl": "",
            "data": {},
        },
    ]

    httpretty.register_uri(
        httpretty.GET,
        "https://grafana.ci.uktrade.digital/" "api/annotations?alertId=1",
        body=json.dumps(grafana),
    )
    return
