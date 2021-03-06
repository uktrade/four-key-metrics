import os

from four_key_metrics.gateways.jenkins import JenkinsBuilds
from four_key_metrics.gateways.github import GitHubCommits
from four_key_metrics.use_case.generate_lead_time_metrics import (
    GenerateLeadTimeMetrics,
    ProjectSummariser,
)
from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)


class UseCaseFactory:
    def create(self, name):
        use_cases = {
            "generate_lead_time_metrics": GenerateLeadTimeMetrics(
                ProjectSummariser(
                    JenkinsBuilds(
                        os.getenv(
                            "DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/"
                        )
                    ),
                    GitHubCommits(),
                )
            ),
            "generate_mean_time_to_restore": GenerateMeanTimeToRestore(),
        }

        if name not in use_cases:
            raise Exception(f"Use Case {name} not found. Check UseCaseFactory")

        return use_cases[name]
