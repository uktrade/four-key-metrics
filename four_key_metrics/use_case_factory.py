import os

from four_key_metrics.gateways import JenkinsBuilds, GitHubCommits
from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics, ProjectSummariser


class UseCaseFactory:
    def create(self, name):
        use_cases = {
            'generate_lead_time_metrics': GenerateLeadTimeMetrics(
                ProjectSummariser(
                    JenkinsBuilds(
                        os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
                    ),
                    GitHubCommits()
                )
            )
        }
        return use_cases[name]
