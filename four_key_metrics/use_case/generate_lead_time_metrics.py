import os
import statistics
from datetime import datetime, timedelta
from typing import Protocol


class GenerateLeadTimeMetricsPresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def failure(self, project):
        ...

    def success(self, repository, environment, lead_time_mean_average, lead_time_standard_deviation):
        ...


class GenerateLeadTimeMetrics:
    def __init__(self, project_summariser):
        self._project_summariser = project_summariser

    def __call__(self, projects, presenter: GenerateLeadTimeMetricsPresenter):
        self._presenter = presenter
        try:
            self._presenter.begin()
            self._write_metrics_for_projects(projects)
        finally:
            self._presenter.end()

    def _write_metrics_for_projects(self, projects):
        for project in projects:
            response = self._project_summariser.get_summary(
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
                self._presenter.failure(project['repository'])
            else:
                self._output_build_commit_metrics(
                    project=project, response=response
                )
                self._presenter.success(
                    project["repository"],
                    project["environment"],
                    response["lead_time_mean_average"],
                    response["lead_time_standard_deviation"]
                )

    def _output_build_commit_metrics(self, project, response):
        for build in response["builds"]:
            for commit in build.commits:
                self._presenter.add(
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


class ProjectSummariser:
    def __init__(self, jenkins, github):
        self._jenkins = jenkins
        self._github = github

    def get_summary(
        self, jenkins_job, github_organisation, github_repository, environment
    ):
        jenkins_builds = self._jenkins.get_jenkins_builds(jenkins_job, environment)
        jenkins_builds.sort(key=lambda b: b.finished_at)
        if len(jenkins_builds) < 2:
            return self._build_summary()
        self._update_last_build_git_reference(
            github_organisation, github_repository, jenkins_builds
        )
        lead_times = self.calculate_lead_times(jenkins_builds)
        return self._build_summary(
            True,
            self.get_lead_time_mean_average(jenkins_builds, lead_times),
            self.get_lead_time_standard_deviation(jenkins_builds, lead_times),
            jenkins_builds,
        )

    def calculate_lead_times(self, builds):
        lead_times = []
        for build in builds:
            for commit in build.commits:
                commit.lead_time = build.finished_at - commit.timestamp
                lead_times.append(commit.lead_time)
        return lead_times

    def _update_last_build_git_reference(
        self,
        github_organisation,
        github_repository,
        jenkins_builds,
    ):
        last_build = jenkins_builds.pop(0)
        excluded_hashes = os.environ["EXCLUDED_DEPLOYMENT_HASHES"]
        for build in jenkins_builds:
            self._update_with_exclusion_builds_with_git_reference(
                github_organisation,
                github_repository,
                last_build,
                excluded_hashes,
                build,
            )
            last_build = build

    def _update_with_exclusion_builds_with_git_reference(
        self, github_organisation, github_repository, last_build, excluded_hashes, build
    ):
        if build.git_reference not in excluded_hashes:
            build.commits = self._github.get_commits_between(
                organisation=github_organisation,
                repository=github_repository,
                base=last_build.git_reference,
                head=build.git_reference,
            )
        build.set_last_build_git_reference(last_build.git_reference)

    def _build_summary(
        self,
        is_success: bool = False,
        lead_time_mean_average: str | None = None,
        lead_time_standard_deviation: str | None = None,
        builds: list = None,
    ):
        return {
            "successful": is_success,
            "lead_time_mean_average": lead_time_mean_average,
            "lead_time_standard_deviation": lead_time_standard_deviation,
            "builds": builds,
        }

    def get_lead_time_mean_average(self, builds, lead_times):
        if self._no_builds(builds):
            return None
        return sum(lead_times) / len(lead_times)

    def get_lead_time_standard_deviation(self, builds, lead_times):
        if self._no_builds(builds):
            return None
        return statistics.pstdev(lead_times)

    def _no_builds(self, builds) -> bool:
        return len(builds) == 0