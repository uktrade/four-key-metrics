from four_key_metrics.metrics_calculator import MetricsCalculator


class GetLeadTimeForProject(object):
    def __init__(self, get_commits_between, get_jenkins_builds):
        self.get_jenkins_builds = get_jenkins_builds
        self.get_commits_between = get_commits_between

    def __call__(self,
                 jenkins_job,
                 github_organisation,
                 github_repository):
        jenkins_builds = self.get_jenkins_builds(jenkins_job)
        if len(jenkins_builds) < 2:
            return {
                'successful': False,
                'lead_time_mean_average': None,
                'lead_time_standard_deviation': None
            }

        commits = self.get_commits_between(
            organisation=github_organisation,
            repository=github_repository,
            base=jenkins_builds[0].git_reference,
            head=jenkins_builds[-1].git_reference
        )

        calculator = MetricsCalculator()
        calculator.add_deploy(timestamp=jenkins_builds[-1].finished_at, commit_timestamps=list(map(lambda x: x.timestamp, commits)))

        return {
            'successful': True,
            'lead_time_mean_average': calculator.get_lead_time_mean_average(),
            'lead_time_standard_deviation': calculator.get_lead_time_standard_deviation()
        }

