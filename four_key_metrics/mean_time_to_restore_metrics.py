import os
import requests
from datetime import timedelta, datetime
from pprint import pprint
from four_key_metrics.all_builds import AllBuilds
from four_key_metrics.data_presenters import (
    DataPresenter,
)


def get_pingdom_id_for_check_names(pingdom_check_names):
    response = requests.get(
        "https://api.pingdom.com/api/3.1/checks/",
        headers={"Authorization": "Bearer " + (os.environ["PINGDOM_TOKEN"])},
        timeout=5,
    )
    if response.status_code != 200:
        print(
            f"{response.reason} [{response.status_code}] "
            f"whilst loading {response.url}"
        )
        if response.status_code == 404:
            print("Check your project's job name.")
        return {}

    body = response.json()
    if len(body["checks"]) == 0:
        return {}

    check_ids = {
        check["name"]: check["id"]
        for check in body["checks"]
        if check["name"] in pingdom_check_names
    }

    if len(check_ids) != len(pingdom_check_names):
        print("WARNING: Not all Pingdom checks found. Check for typos.")

    return check_ids


def get_pingdom_analysis(pingdom_check_id):
    response = requests.get(
        f"https://api.pingdom.com/api/3.1/analysis/{pingdom_check_id}",
        headers={"Authorization": "Bearer " + (os.environ["PINGDOM_TOKEN"])},
        timeout=5,
    )
    if response.status_code != 200:
        print(
            f"{response.reason} [{response.status_code}] "
            f"whilst loading {response.url}"
        )
        if response.status_code == 404:
            print("Check your pingdom check id.")
        return {}

    body = response.json()
    if len(body["analysis"]) == 0:
        return {}

    return body["analysis"]


def get_pingdom_analysis_details(pingdom_check_id, analysis_id):
    response = requests.get(
        f"https://api.pingdom.com/api/3.1/analysis/{pingdom_check_id}/{analysis_id}",
        headers={"Authorization": "Bearer " + (os.environ["PINGDOM_TOKEN"])},
        timeout=5,
    )
    if response.status_code != 200:
        print(
            f"{response.reason} [{response.status_code}] "
            f"whilst loading {response.url}"
        )
        if response.status_code == 404:
            print("Check your pingdom check id.")
        return {}

    body = response.json()

    return body


def get_mean_time_to_restore_for_pingdom_id_and_analysis_id(
    pingdom_check_id, analysis_id
):
    analysis_details = get_pingdom_analysis_details(pingdom_check_id, analysis_id)
