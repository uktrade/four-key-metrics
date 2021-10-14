import base64

import httpretty


def assert_authorization_is(authentication):
    basic_string = base64.b64encode(authentication).decode()
    actual_header = httpretty.last_request().headers['Authorization']
    expected_header = 'Basic %s' % basic_string
    assert actual_header == expected_header
