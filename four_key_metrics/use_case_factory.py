import os

from four_key_metrics.gateways import JenkinsBuilds
from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics


class UseCaseFactory:
    def create(self, name):
        use_cases = {
            'generate_lead_time_metrics': GenerateLeadTimeMetrics(JenkinsBuilds(
                os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/")
            ))
        }
        return use_cases[name]
