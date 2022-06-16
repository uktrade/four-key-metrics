from datetime import datetime, timedelta
from typing import List
import os

import requests
from four_key_metrics.domain_models import Outage


class GrafanaAlertAnnotation:
    def _get_alert_uids_from_names(self, alert_names):
        response = requests.get(
            "https://grafana.ci.uktrade.digital/api/alerts",
            headers={"Authorization": "Bearer " + (os.environ["GRAFANA_TOKEN"])},
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
        if len(body) == 0:
            return {}

        alert_uids = {
            alert["name"]: alert["id"] for alert in body if alert["name"] in alert_names
        }

        if len(alert_uids) != len(alert_names):
            print("WARNING: Not all Grafana alert names found. Check for typos.")

        return alert_uids

    def _sort_annotations_by_ascending_time(self, annotations) -> List[dict]:
        return sorted(annotations, key=(lambda annotation: annotation["created"]))

    def _get_grafana_alert_annotations(self, grafana_alert_id, from_timestamp=None):
        if not from_timestamp:
            from_timestamp = int(
                datetime.timestamp(datetime.now() - timedelta(days=180))
            )
        response = requests.get(
            f"https://grafana.ci.uktrade.digital/api/annotations?alertId={grafana_alert_id}&from={from_timestamp}",
            headers={"Authorization": "Bearer " + (os.environ["GRAFANA_TOKEN"])},
            timeout=5,
        )
        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your grafana alert id.")
            return {}

        return response.json()

    def _create_outages_from_annotations(self, annotations, alert_name):
        outages = []
        ongoing_outage = None
        for annotation in annotations:
            state_is_ok = annotation["newState"] == "ok"
            if not state_is_ok and not ongoing_outage:
                ongoing_outage = annotation
            elif state_is_ok and ongoing_outage:
                outages.append(
                    Outage(
                        source="grafana",
                        project=annotation["alertName"],
                        environment="-",
                        grafana_alert_name=ongoing_outage["id"],
                        down_timestamp=round(ongoing_outage["time"] / 1000),
                        up_timestamp=round(annotation["timeEnd"] / 1000),
                    )
                )
                ongoing_outage = None
            else:
                pass
        return outages

    def get_grafana_outages(self, grafana_alert_names):
        grafana_outages = []
        alert_uids = self._get_alert_uids_from_names(grafana_alert_names)
        for alert_name, alert_uid in alert_uids.items():
            annotations = self._get_grafana_alert_annotations(alert_uid)
            ascending_annotations = self._sort_annotations_by_ascending_time(
                annotations
            )
            outages = self._create_outages_from_annotations(
                ascending_annotations, alert_name
            )
            grafana_outages.extend(outages)

        return grafana_outages
