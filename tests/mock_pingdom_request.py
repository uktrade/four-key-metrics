import json

import httpretty


def httpretty_404_no_pingdom_checks():
    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/checks/",
        status=404,
    )
    return

def httpretty_503_no_pingdom_checks():
    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/checks/",
        status=503,
    )
    return

def httpretty_no_checks():
    pingdom = {
        "checks": [],
        "counts": {"total": 0, "limited": 0, "filtered": 0},
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/checks/",
        body=json.dumps(pingdom),
    )
    return


def httpretty_checks():
    pingdom = {
        "checks": [
            {
                "id": 3966721,
                "created": 1511194948,
                "name": "uk.gov.trade.datahub.api",
                "hostname": "www.datahub.trade.gov.uk",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "false",
                "lasterrortime": 1651051310,
                "lasttesttime": 1651572289,
                "lastresponsetime": 320,
                "lastdownstart": 1651051309,
                "lastdownend": 1651051369,
                "status": "up",
            },
            {
                "id": 4946807,
                "created": 1545143412,
                "name": "Data Hub P1",
                "hostname": "www.datahub.trade.gov.uk",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "true",
                "lasterrortime": 1649110469,
                "lasttesttime": 1651572269,
                "lastresponsetime": 218,
                "lastdownstart": 1649109749,
                "lastdownend": 1649110529,
                "status": "up",
            },
            {
                "id": 3516241,
                "created": 1504790505,
                "name": "cert check panic 7 day",
                "hostname": "s3-eu-west-1.amazonaws.com",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "false",
                "lasterrortime": 1533033907,
                "lasttesttime": 1533033907,
                "lastresponsetime": 0,
                "lastdownstart": 1533033787,
                "status": "paused",
            },
            {
                "id": 5654644,
                "created": 1576234268,
                "name": "Data Hub P2",
                "hostname": "www.datahub.trade.gov.uk",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "true",
                "lasterrortime": 1651219794,
                "lasttesttime": 1651572283,
                "lastresponsetime": 645,
                "lastdownstart": 1651219783,
                "lastdownend": 1651219843,
                "status": "up",
            },
            {
                "id": 4709189,
                "created": 1531997684,
                "name": "Domestic UI Staging",
                "hostname": "great.staging.uktrade.digital",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "false",
                "lasterrortime": 1651572299,
                "lasttesttime": 1651572299,
                "lastresponsetime": 0,
                "lastdownstart": 1619443963,
                "lastdownend": 1651572299,
                "status": "down",
            },
            {
                "id": 4855100,
                "created": 1541067529,
                "name": "SSO Staging",
                "hostname": "great.staging.uktrade.digital",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "true",
                "lasterrortime": 1632785550,
                "lasttesttime": 1651572270,
                "lastresponsetime": 780,
                "lastdownstart": 1632785490,
                "lastdownend": 1632785610,
                "status": "up",
            },
        ],
        "counts": {"total": 6, "limited": 6, "filtered": 1},
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/checks/",
        body=json.dumps(pingdom),
    )
    return


def httpretty_checks_p1():
    pingdom = {
        "checks": [
            {
                "id": 4946807,
                "created": 1545143412,
                "name": "Data Hub P1",
                "hostname": "www.datahub.trade.gov.uk",
                "resolution": 1,
                "type": "http",
                "ipv6": "false",
                "verify_certificate": "true",
                "lasterrortime": 1649110469,
                "lasttesttime": 1651572269,
                "lastresponsetime": 218,
                "lastdownstart": 1649109749,
                "lastdownend": 1649110529,
                "status": "up",
            },
        ],
        "counts": {"total": 1, "limited": 1, "filtered": 1},
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/checks",
        body=json.dumps(pingdom),
    )
    return


def httpretty_summary_outage_p1():
    pingdom = {
        "summary": {
            "states": [
                {"status": "up", "timefrom": 1636377304, "timeto": 1637168609},
                {"status": "down", "timefrom": 1637168609, "timeto": 1637172329},
                {"status": "up", "timefrom": 1637172329, "timeto": 1641082589},
                {"status": "unknown", "timefrom": 1641082589, "timeto": 1641082949},
                {"status": "down", "timefrom": 1641082949, "timeto": 1641083189},
            ]
        }
    }

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/summary.outage/4946807",
        body=json.dumps(pingdom),
    )
    return


def httpretty_summary_outage_status(status=404):
    pingdom = {"summary": {"states": []}}

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/summary.outage/4946807",
        status=status,
    )
    return


def httpretty_summary_outage_blank():
    pingdom = {"summary": {"states": []}}

    httpretty.register_uri(
        httpretty.GET,
        "https://api.pingdom.com/" "api/3.1/summary.outage/4946807",
        body=json.dumps(pingdom),
    )
    return
