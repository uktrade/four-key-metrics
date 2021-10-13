from four_key_metrics.metrics_calculator import MetricsCalculator


class GetLeadTimeForProject(object):
    def __init__(self, get_commits_between, get_jenkins_builds):
        self.get_jenkins_builds = get_jenkins_builds
        self.get_commits_between = get_commits_between

    def __call__(self,
                 jenkins_job,
                 github_organisation,
                 github_repository):
        if len(self.get_jenkins_builds('')) < 2:
            return {
                'successful': False,
                'lead_time_mean_average': None,
                'lead_time_standard_deviation': None
            }

        builds = self.get_jenkins_builds(job=None)

        commits = self.get_commits_between(
            organisation=None,
            repository=None,
            base=None,
            head=None
        )

        calculator = MetricsCalculator()
        calculator.add_deploy(timestamp=builds[-1].finished_at, commit_timestamps=list(map(lambda x: x.timestamp, commits)))

        return {
            'successful': True,
            'lead_time_mean_average': calculator.get_lead_time_mean_average(),
            'lead_time_standard_deviation': calculator.get_lead_time_standard_deviation()
        }

