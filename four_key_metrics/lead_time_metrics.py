import os
from datetime import timedelta, datetime
from pprint import pprint
import csv
from four_key_metrics.all_builds import AllBuilds


def generate_lead_time_metrics(projects):

    all_builds = AllBuilds(
        os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
    )
    csv_filename = f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv"

    with open(
        csv_filename,
        "w",
        newline="",
    ) as csvfile:
        fieldnames = [
            "repository",
            "build_commit_hash",  # "Deployment hash"
            "build_timestamp",
            "build_time",
            "commit_hash",  # "Deployment timestamp",
            "commit_timestamp",
            "commit_time",
            "commit_lead_time_days",
            "commit_lead_time",
            "previous_build_commit_hash",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        _write_metrics_for_projects(projects, all_builds, writer)

    pprint(f"Detailed metrics stored in {csv_filename}")


def _write_metrics_for_projects(projects, all_builds, writer):
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
            _write_build_metrics(writer, project, response)

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


def _write_build_metrics(writer, project, response):
    for build in response["builds"]:
        build
        for commit in build.commits:
            writer.writerow(
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
