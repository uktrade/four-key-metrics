class GetLeadTimeForProject(object):
    def __init__(self, get_commits_between, get_jenkins_builds):
        self.get_jenkins_builds = get_jenkins_builds
        self.get_commits_between = get_commits_between

    def __call__(self,
                 jenkins_job,
                 github_organisation,
                 github_repository):
        return {
            'successful': False,
            'lead_time_mean_average': None,
            'lead_time_standard_deviation': None
        }
