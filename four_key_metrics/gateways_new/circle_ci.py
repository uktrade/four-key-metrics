
import os
from typing import List
import requests
from four_key_metrics.domain_models import Outage

from four_key_metrics.utilities import iso_string_to_timestamp


class CircleCiRuns:
    def _get_circle_ci_runs(self, project, workflow) -> List[dict]:

        response = requests.get(
            f"https://circleci.com/api/v2/insights/{project}/workflows/{workflow}",
            headers={"Authorization": "Bearer " + (os.environ["CIRCLE_CI_TOKEN"])},
            timeout=5,
        )

        if response.status_code != 200:
            print(
                f"{response.reason} [{response.status_code}] "
                f"whilst loading {response.url}"
            )
            if response.status_code == 404:
                print("Check your project or workflow name")
            return []

        body = response.json()
        return body["items"]

    def _sort_runs_by_ascending_time(self, runs) -> List[dict]:
        return sorted(runs, key=(lambda run: run["created_at"]))

    def get_circle_ci_outages(self, projects: dict) -> List[Outage]:
        outages = []
        for project, workflows in projects.items():
            for workflow in workflows:
                runs = self._get_circle_ci_runs(project, workflow)
                ascending_runs = self._sort_runs_by_ascending_time(runs)
                outages.extend(self._create_outages_from_runs(ascending_runs, project))
        return outages

    def _create_outages_from_runs(self, runs, project):
        outages = []
        failed_run_starting_outage = None
        for run in runs:
            is_succcessful_run = run["status"] == "success"
            if not is_succcessful_run and not failed_run_starting_outage:
                failed_run_starting_outage = run
            elif is_succcessful_run and failed_run_starting_outage:
                outages.append(
                    Outage(
                        source="circle_ci",
                        project=project,
                        environment=run["branch"],
                        circle_ci_failed_run_id=failed_run_starting_outage["id"],
                        down_timestamp=round(
                            iso_string_to_timestamp(
                                failed_run_starting_outage["created_at"]
                            )
                        ),
                        up_timestamp=round(iso_string_to_timestamp(run["stopped_at"])),
                    )
                )
                failed_run_starting_outage = None
            else:
                pass
        return outages
