import base64

import httpretty


def test_check_average_and_standard_deviation():
    output = {
        "average": "4 days, 10:11:19.988286",
        "project": "data-hub-frontend",
        "standard_deviation": "4 days, 23:57:23.917895",
    }


def test_can_get_jenkins_builds(authentication):
    basic_string = base64.b64encode(authentication).decode()
    actual_header = httpretty.last_request().headers["Authorization"]
    expected_header = "Basic %s" % basic_string
    assert actual_header == expected_header
