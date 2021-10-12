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


def test_can_get_no_lead_time():
    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=lambda organisation, repository, base, head: [],
        get_jenkins_builds=lambda job: []
    )
    response = get_lead_time_for_project(
        jenkins_job='no/builds',
        github_organisation='has-no-commits',
        github_repository='commit-less'
    )
    assert not response['successful']
    assert response['lead_time_mean_average'] is None
    assert response['lead_time_standard_deviation'] is None
