import json
import httpretty

def httpretty_no_circle_ci_runs():
    response = {
        "next_page_token" : 'null',
        "items" : [ ]
        }

    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )

    return 