from datetime import datetime, timedelta
import os

import requests
from four_key_metrics.domain_models import Outage


class PingdomOutages:
    def _get_pingdom_id_for_check_names(self, pingdom_check_names):
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

    def _get_pingdom_outage_summary(self, pingdom_check_id, from_timestamp=None):
        if not from_timestamp:
            from_timestamp = int(
                datetime.timestamp(datetime.now() - timedelta(days=180))
            )
        response = requests.get(
            f"https://api.pingdom.com/api/3.1/summary.outage/{pingdom_check_id}?from={from_timestamp}",
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

        return [
            {"down_timestamp": outage["timefrom"], "up_timestamp": outage["timeto"]}
            for outage in body["summary"]["states"]
            if outage["status"] == "down"
        ]

    def get_pingdom_outages(self, pingdom_check_names):
        pingdom_outages = []
        pingdom_checks = self._get_pingdom_id_for_check_names(pingdom_check_names)
        for name, pingdom_check_id in pingdom_checks.items():
            outages = self._get_pingdom_outage_summary(pingdom_check_id)
            for outage in outages:
                pingdom_outages.append(
                    Outage(
                        source="pingdom",
                        environment="production",
                        project=name,
                        pingdom_check_id=pingdom_check_id,
                        down_timestamp=outage["down_timestamp"],
                        up_timestamp=outage["up_timestamp"],
                    )
                )
        return pingdom_outages
