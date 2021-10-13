from datetime import timedelta
from pprint import pprint

from four_key_metrics.github import get_commits_between
from four_key_metrics.jenkins import Jenkins
from four_key_metrics.use_case.get_lead_time_for_project import GetLeadTimeForProject

jenkins = Jenkins('https://jenkins.ci.uktrade.digital/')  # input("Jenkins host (e.g. https://my.host.com/)"))

get_lead_time_for_project = GetLeadTimeForProject(
    get_commits_between=get_commits_between,
    get_jenkins_builds=jenkins.get_jenkins_builds
)
response = get_lead_time_for_project(
    jenkins_job='datahub-fe',  # input("Jenkins job id (e.g. datahub-api)"),
    github_organisation='uktrade',  # input("GitHub org (e.g. uktrade)"),
    github_repository='data-hub-frontend',  # input("GitHub repository (e.g. data-hub-api)"),
    environment='production',  # input("Environment (e.g. production)")
)

pprint(
    {
        'average': str(timedelta(seconds=response['lead_time_mean_average'])),
        'standard_deviation': str(timedelta(seconds=response['lead_time_standard_deviation'])),
    }
)
