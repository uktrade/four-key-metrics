from datetime import datetime
import os
from typing import List, Protocol

from four_key_metrics.gateways.circle_ci import CircleCiRuns
from four_key_metrics.gateways.grafana import GrafanaAlertAnnotation
from four_key_metrics.gateways.jenkins import JenkinsBuilds
from four_key_metrics.gateways.pingdom import PingdomOutages


class GenerateMeanTimeToRestorePresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def failure(self, pingdom_check_names):
        ...

    def success(self, source, mean_time_to_restore_average, outages_count):
        ...


class GenerateMeanTimeToRestore:
    def __init__(self):
        return

    def __call__(
        self,
        pingdom_check_names,
        jenkins_jobs,
        circle_ci_projects,
        grafana_alert_names,
        presenter: GenerateMeanTimeToRestorePresenter,
    ):
        self._presenter = presenter
        try:
            self._presenter.begin()
            self._get_pingdom_mean_time_to_restore(pingdom_check_names)
            self._get_jenkins_mean_time_to_restore(jenkins_jobs)
            self._get_circle_ci_mean_time_to_restore(circle_ci_projects)
            self._get_grafana_mean_time_to_restore(grafana_alert_names)
        finally:
            self._presenter.end()

    def _get_pingdom_mean_time_to_restore(self, check_names: List[str]):
        all_outages = PingdomOutages().get_pingdom_outages(check_names)
        return self._add_outages_to_presenter(all_outages, "pingdom")

    def _get_jenkins_mean_time_to_restore(self, jenkins_jobs: List[str]):
        jenkins_builds = JenkinsBuilds(
            os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
        )
        all_outages = jenkins_builds.get_jenkins_outages(jenkins_jobs)
        return self._add_outages_to_presenter(all_outages, "jenkins")

    def _get_circle_ci_mean_time_to_restore(self, circle_ci_projects: dict):
        all_outages = CircleCiRuns().get_circle_ci_outages(circle_ci_projects)
        return self._add_outages_to_presenter(all_outages, "circle_ci")

    def _get_grafana_mean_time_to_restore(self, grafana_alert_names: List[str]):
        all_outages = GrafanaAlertAnnotation().get_grafana_outages(grafana_alert_names)
        return self._add_outages_to_presenter(all_outages, "grafana")

    def _add_outages_to_presenter(self, outages, source_name):
        total_time_to_restore = 0
        for outage in outages:
            total_time_to_restore += outage.seconds_to_restore
            self._presenter.add(
                {
                    "source": outage.source,
                    "project": outage.project,
                    "environment": outage.environment,
                    "down_timestamp": outage.down_timestamp,
                    "down_time": datetime.fromtimestamp(outage.down_timestamp).strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "up_timestamp": outage.up_timestamp,
                    "up_time": datetime.fromtimestamp(outage.up_timestamp).strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "seconds_to_restore": outage.seconds_to_restore,
                }
            )

        if not outages:
            self._presenter.failure(source_name)
            return None

        mean_time_to_restore = round(total_time_to_restore / len(outages))
        self._presenter.success(source_name, mean_time_to_restore, len(outages))
        return mean_time_to_restore
