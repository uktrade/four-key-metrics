import json
import httpretty

basic_circle_ci_project_configuration = [
    {
        "project": "test-project",
        "workflows": ["test-workflow"],
        "branches": ["master"],
    },
]

# four runs which should turn into 2 outages
four_mock_runs = [
    {
        "id": "59ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        "duration": 731,
        "status": "success",
        "created_at": "2022-05-24T10:13:58.411Z",
        "stopped_at": "2022-05-24T10:26:09.509Z",
        "credits_used": 25165,
        "branch": "master",
        "is_approval": "false",
    },
    {
        "id": "69ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        "duration": 731,
        "status": "failed",
        "created_at": "2022-05-23T10:13:58.411Z",
        "stopped_at": "2022-05-23T10:26:09.509Z",
        "credits_used": 25165,
        "branch": "master",
        "is_approval": "false",
    },
    {
        "id": "79ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        "duration": 731,
        "status": "success",
        "created_at": "2022-05-22T10:13:58.411Z",
        "stopped_at": "2022-05-22T10:26:09.509Z",
        "credits_used": 25165,
        "branch": "master",
        "is_approval": "false",
    },
    {
        "id": "89ad3361-99eb-44a4-8c97-03c0b62eb3f2",
        "duration": 731,
        "status": "failed",
        "created_at": "2022-05-20T10:13:58.411Z",
        "stopped_at": "2022-05-20T10:26:09.509Z",
        "credits_used": 25165,
        "branch": "master",
        "is_approval": "false",
    },
]


def httpretty_circle_ci_no_runs():
    response = {"next_page_token": "null", "items": []}

    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )

    return


def httpretty_404_not_found_circle_ci_runs():
    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-wrong-project/workflows/test-workflow",
        status=404,
    )
    return


def httpretty_401_unauthorized_circle_ci_runs():
    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-wrong-project/workflows/test-workflow",
        status=401,
        body=json.dumps({"message": "You must log in first."}),
    )
    return


def httpretty_circle_ci_runs_success():
    response = {"items": four_mock_runs}

    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )
    return


def httpretty_circle_ci_runs_success_other_project():
    response = {"items": four_mock_runs}

    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/other-project/workflows/test-workflow",
        body=json.dumps(response),
    )
    return


def httpretty_circle_ci_runs_success_other_workflow():
    response = {"items": four_mock_runs}

    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/other-workflow",
        body=json.dumps(response),
    )
    return


def httpretty_circle_ci_runs_all_failures():
    response = {
        "items": [
            {
                "id": "19ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "failed",
                "created_at": "2022-05-25T10:13:58.411Z",
                "stopped_at": "2022-05-25T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "29ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "failed",
                "created_at": "2022-05-24T10:13:58.411Z",
                "stopped_at": "2022-05-24T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "39ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "failed",
                "created_at": "2022-05-23T10:13:58.411Z",
                "stopped_at": "2022-05-23T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
        ]
    }
    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )
    return


def httpretty_circle_ci_runs_all_successes():
    response = {
        "items": [
            {
                "id": "19ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "success",
                "created_at": "2022-05-25T10:13:58.411Z",
                "stopped_at": "2022-05-25T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "29ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "success",
                "created_at": "2022-05-24T10:13:58.411Z",
                "stopped_at": "2022-05-24T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "39ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "success",
                "created_at": "2022-05-23T10:13:58.411Z",
                "stopped_at": "2022-05-23T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
        ]
    }
    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )
    return


def httpretty_circle_ci_runs_two_failures_in_a_row():
    response = {
        "items": [
            {
                "id": "19ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "success",
                "created_at": "2022-05-25T10:13:58.411Z",
                "stopped_at": "2022-05-25T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "29ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "failed",
                "created_at": "2022-05-24T10:13:58.411Z",
                "stopped_at": "2022-05-24T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
            {
                "id": "39ad3361-99eb-44a4-8c97-03c0b62eb3f2",
                "duration": 731,
                "status": "failed",
                "created_at": "2022-05-23T10:13:58.411Z",
                "stopped_at": "2022-05-23T10:26:09.509Z",
                "credits_used": 25165,
                "branch": "master",
                "is_approval": "false",
            },
        ]
    }
    httpretty.register_uri(
        httpretty.GET,
        "https://circleci.com/api/v2/insights/test-project/workflows/test-workflow",
        body=json.dumps(response),
    )
    return
