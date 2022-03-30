from datetime import timedelta, date, datetime
from pprint import pprint
import csv

from four_key_metrics.github import get_commits_between
from four_key_metrics.jenkins import Jenkins
from four_key_metrics.use_case.get_lead_time_for_project import GetLeadTimeForProject

jenkins = Jenkins(
    "https://jenkins.ci.uktrade.digital/"
)  # input("Jenkins host (e.g. https://my.host.com/)"))

get_lead_time_for_project = GetLeadTimeForProject(
    get_commits_between=get_commits_between,
    get_jenkins_builds=jenkins.get_jenkins_builds,
)

projects = [
    {"job": "datahub-fe", "repository": "data-hub-frontend"},
    {"job": "datahub-api", "repository": "data-hub-api"},
]

with open(
    f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv",
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
        "commit_lead_timestamp",
        "commit_lead_time",
        "previous_build_commit_hash",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for project in projects:
        response = get_lead_time_for_project(
            jenkins_job=project["job"],  # input("Jenkins job id (e.g. datahub-api)"),
            github_organisation="uktrade",  # input("GitHub org (e.g. uktrade)"),
            github_repository=project[
                "repository"
            ],  # input("GitHub repository (e.g. data-hub-api)"),
            environment="production",  # input("Environment (e.g. production)")
        )

        for deploy in response["deploys"]:
            for commit in deploy["commits"]:
                writer.writerow(
                    {
                        "repository": project["repository"],
                        "build_commit_hash": deploy["build_commit_hash"],
                        "build_timestamp": deploy["build_timestamp"],
                        "build_time": datetime.fromtimestamp(
                            deploy["build_timestamp"]
                        ).strftime("%d/%m/%Y %H:%M:%S"),
                        "commit_hash": commit.sha,
                        "commit_timestamp": commit.timestamp,
                        "commit_time": datetime.fromtimestamp(
                            commit.timestamp
                        ).strftime("%d/%m/%Y %H:%M:%S"),
                        "commit_lead_timestamp": commit.lead_time,
                        "commit_lead_time": str(timedelta(seconds=commit.lead_time)),
                        "previous_build_commit_hash": deploy[
                            "previous_build_commit_hash"
                        ],
                    }
                )

        pprint(
            {
                "project": project["repository"],
                "average": str(timedelta(seconds=response["lead_time_mean_average"])),
                "standard_deviation": str(
                    timedelta(seconds=response["lead_time_standard_deviation"])
                ),
            }
        )
