from four_key_metrics.use_case.get_lead_time_for_project import GetLeadTimeForProject


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
