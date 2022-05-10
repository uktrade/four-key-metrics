import os

from four_key_metrics.gateways import JenkinsBuilds, GitHubCommits
from four_key_metrics.use_case.generate_lead_time_metrics import (
    GenerateLeadTimeMetrics,
    ProjectSummariser,
)
from four_key_metrics.use_case.generate_mean_time_to_restore import (
    GenerateMeanTimeToRestore,
)
from four_key_metrics.constants import PINGDOM_CHECK_NAMES


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
