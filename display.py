from cmd import Cmd
import os
from datetime import timedelta, datetime
from pprint import pprint
import csv
from dotenv import load_dotenv

from four_key_metrics.all_builds import AllBuilds

load_dotenv()


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

        for project in projects:
            # create an AllBuilds class which then gets the lead time for the projects
            # E.g.
            # all_builds = AllBuilds(project=project)
            # all_builds.get_average_lead_time()
            response = all_builds.add_project(
                jenkins_job=project[
                    "job"
                ],  # input("Jenkins job id (e.g. datahub-api)"),
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
                for build in response["builds"]:
                    build
                    for commit in build.commits:
                        writer.writerow(
                            {
                                "repository": project["repository"],
                                "build_commit_hash": build.git_reference,
                                "build_timestamp": build.finished_at,
                                "build_time": datetime.fromtimestamp(
                                    build.finished_at
                                ).strftime("%d/%m/%Y %H:%M:%S"),
                                "commit_hash": commit.sha,
                                "commit_timestamp": commit.timestamp,
                                "commit_time": datetime.fromtimestamp(
                                    commit.timestamp
                                ).strftime("%d/%m/%Y %H:%M:%S"),
                                "commit_lead_time_days": commit.lead_time / 86400,
                                "commit_lead_time": str(
                                    timedelta(seconds=commit.lead_time)
                                ),
                                "previous_build_commit_hash": build.last_build_git_reference,
                            }
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

    print(f"Detailed metrics stored in {csv_filename}")


def remove_generated_reports(extension=".csv"):
    for file in os.listdir("."):
        if file.endswith(extension):
            os.remove(file)
            print(os.path.join("Removed ./", file))


class DisplayShell(Cmd):
    """Command allowing specific reports to be generated through actions"""

    intro = "Welcome to the key metrics shell. Type help or ?.\n"
    prompt = "(type <topic> to generate report) "

    def do_ltm(self, arg):
        """Generate lead time time metrics

        Args:
            arg (json): TODO: Figure out what can be passed to make this more
            configurable
        """
        self.do_lead_time_metrics(arg)

    def do_lead_time_metrics(self, arg):
        """Generate lead time time metrics

        Args:
            arg (json): TODO: Figure out what can be passed to make this more
            configurable
        """
        projects = [
            {
                "job": "datahub-api",
                "repository": "data-hub-api",
                "environment": "production",
            },
            {
                "job": "datahub-fe",
                "repository": "data-hub-frontend",
                "environment": "production",
            },
        ]
        generate_lead_time_metrics(projects)

    def do_remove_reports(self, arg):
        """Clean up generated reports by supported output types, e.g. .csv

        Args:
            arg (string): Defaults to '.csv' but can be overriden to support
                '.json, '.txt', '.xml' or other supported types
        """
        fileExtension = ".csv"
        if arg:
            fileExtension = arg
        print("searching ", fileExtension)
        remove_generated_reports(fileExtension)


if __name__ == "__main__":

    DisplayShell().cmdloop()
