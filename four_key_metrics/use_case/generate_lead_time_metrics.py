import os
from datetime import datetime, timedelta
from pprint import pprint

from four_key_metrics.all_builds import AllBuilds
from four_key_metrics.data_presenters import DataPresenter


class GenerateLeadTimeMetrics:
    def __init__(self):
        self.all_builds = AllBuilds(
            os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
        )

    def generate_lead_time_metrics(self, projects: dict, data_presenter: DataPresenter):
        self.data_presenter = data_presenter
        try:
            self.data_presenter.begin()
            self._write_metrics_for_projects(
                projects=projects, all_builds=self.all_builds
            )
        finally:
            self.data_presenter.end()

    def _write_metrics_for_projects(self, projects, all_builds):
        for project in projects:
            response = all_builds.add_project(
                jenkins_job=project["job"],
                github_organisation="uktrade",
                github_repository=project[
                    "repository"
                ],
                environment=project[
                    "environment"
                ],
            )
            if not response["successful"]:
                self.data_presenter.failure(project['repository'])
            else:
                self._output_build_commit_metrics(
                    project=project, response=response
                )

                pprint(
                    {
                        "project": project["repository"],
                        "environment": project["environment"],
                        "average": str(
                            timedelta(seconds=response["lead_time_mean_average"])
                        ),
                        "standard_deviation": str(
                            timedelta(seconds=response["lead_time_standard_deviation"])
                        ),
                    },
                    sort_dicts=False,
                )

    def _output_build_commit_metrics(self, project, response):
        for build in response["builds"]:
            for commit in build.commits:
                self.data_presenter.add(
                    {
                        "repository": project["repository"],
                        "build_commit_hash": build.git_reference,
                        "build_timestamp": build.finished_at,
                        "build_time": datetime.fromtimestamp(build.finished_at).strftime(
                            "%d/%m/%Y %H:%M:%S"
                        ),
                        "commit_hash": commit.sha,
                        "commit_timestamp": commit.timestamp,
                        "commit_time": datetime.fromtimestamp(commit.timestamp).strftime(
                            "%d/%m/%Y %H:%M:%S"
                        ),
                        "commit_lead_time_days": commit.lead_time / 86400,
                        "commit_lead_time": str(timedelta(seconds=commit.lead_time)),
                        "previous_build_commit_hash": build.last_build_git_reference,
                    }
                )
