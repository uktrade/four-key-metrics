import os

from four_key_metrics.gateways import JenkinsBuilds
from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics, ProjectSummariser


class UseCaseFactory:
    def create(self, name):
        jenkins = JenkinsBuilds(os.getenv("DIT_JENKINS_URI", "https://jenkins.ci.uktrade.digital/"))
        use_cases = {
            'generate_lead_time_metrics': GenerateLeadTimeMetrics(jenkins, ProjectSummariser(jenkins))
        }
        return use_cases[name]
