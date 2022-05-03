import os
from datetime import datetime, timedelta
from pprint import pprint

from four_key_metrics.all_builds import AllBuilds
from four_key_metrics.data_presenters import DataPresenter

class GenerateLeadTimeMetrics:
    def generate_lead_time_metrics(self, projects: dict, data_presenter: DataPresenter):
        all_builds = AllBuilds(
            os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
        )
        try:
            data_presenter.begin()
            self._write_metrics_for_projects(
                projects=projects, all_builds=all_builds, data_presenter=data_presenter
            )
        finally:
            data_presenter.end()

    def _write_metrics_for_projects(self, projects, all_builds, data_presenter: DataPresenter):
        for project in projects:
            response = all_builds.add_project(
                jenkins_job=project["job"],  # input("Jenkins job id (e.g. datahub-api)"),
                github_organisation="uktrade",  # input("GitHub org (e.g. uktrade)"),
                github_repository=project[
                    "repository"
                ],  # input("GitHub repository (e.g. data-hub-api)"),
                environment=project[
                    "environment"
                ],  # input("Environment (e.g. production)")
            )
            if not response["successful"]:
                pprint(
                    {
                        "project": project["repository"],
                        "average": response["lead_time_mean_average"],
                        "standard_deviation": response["lead_time_standard_deviation"],
                    }
                )
            else:
                self._output_build_commit_metrics(
                    data_presenter=data_presenter, project=project, response=response
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

    def _output_build_commit_metrics(self, data_presenter: DataPresenter, project, response):
        for build in response["builds"]:
            build
            for commit in build.commits:
                data_presenter.add(
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
