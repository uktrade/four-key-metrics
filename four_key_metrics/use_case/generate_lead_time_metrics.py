import os

from four_key_metrics.all_builds import AllBuilds
from four_key_metrics.data_presenters import DataPresenter
from four_key_metrics.lead_time_metrics import _write_metrics_for_projects


class GenerateLeadTimeMetrics:
    def generate_lead_time_metrics(projects: dict, data_presenter: DataPresenter):
        all_builds = AllBuilds(
            os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
        )
        try:
            data_presenter.begin()
            _write_metrics_for_projects(
                projects=projects, all_builds=all_builds, data_presenter=data_presenter
            )
        finally:
            data_presenter.end()
