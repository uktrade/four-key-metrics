import pytest

from four_key_metrics.github import GitCommit
from four_key_metrics.jenkins import Build
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


def test_can_not_get_lead_time_for_one_build():
    build = Build(
        started_at=0,
        finished_at=1,
        successful=True,
        environment='Production',
        git_reference='123456'
    )
    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=lambda organisation, repository, base, head: [],
        get_jenkins_builds=lambda job: [build]
    )
    response = get_lead_time_for_project(
        jenkins_job='no/builds',
        github_organisation='has-no-commits',
        github_repository='commit-less'
    )
    assert not response['successful']
    assert response['lead_time_mean_average'] is None
    assert response['lead_time_standard_deviation'] is None


def test_can_get_lead_time_for_two_builds_one_commit():
    build1 = Build(
        started_at=0,
        finished_at=1,
        successful=True,
        environment='Production',
        git_reference='123456'
    )
    build2 = Build(
        started_at=0,
        finished_at=1,
        successful=True,
        environment='Production',
        git_reference='123457'
    )
    commit = GitCommit(
        timestamp=0
    )
    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=lambda organisation, repository, base, head: [commit],
        get_jenkins_builds=lambda job: [build1, build2]
    )
    response = get_lead_time_for_project(
        jenkins_job='no/builds',
        github_organisation='has-no-commits',
        github_repository='commit-less'
    )
    assert response['successful']
    assert response['lead_time_mean_average'] == 1
    assert response['lead_time_standard_deviation'] == 0


def test_can_get_lead_time_for_two_builds_two_commits():
    build1 = Build(
        started_at=0,
        finished_at=1,
        successful=True,
        environment='Production',
        git_reference='123456'
    )
    build2 = Build(
        started_at=0,
        finished_at=2,
        successful=True,
        environment='Production',
        git_reference='123457'
    )
    commit1 = GitCommit(
        timestamp=0
    )
    commit2 = GitCommit(
        timestamp=0
    )
    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=lambda organisation, repository, base, head: [commit1, commit2],
        get_jenkins_builds=lambda job: [build1, build2]
    )
    response = get_lead_time_for_project(
        jenkins_job='no/builds',
        github_organisation='has-no-commits',
        github_repository='commit-less'
    )
    assert response['successful']
    assert response['lead_time_mean_average'] == 2
    assert response['lead_time_standard_deviation'] == 0


@pytest.mark.parametrize("job", [('no/builds'), 'no/builds2'])
def test_can_pass_parameters_to_get_jenkins_builds_correctly(job):
    spy_calls = []

    def spy(job):
        spy_calls.append(job)
        return [Build(
            started_at=0,
            finished_at=1,
            successful=True,
            environment='Production',
            git_reference='123456'
        ), Build(
            started_at=0,
            finished_at=1,
            successful=True,
            environment='Production',
            git_reference='123456'
        )]

    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=lambda organisation, repository, base, head: [],
        get_jenkins_builds=spy
    )
    get_lead_time_for_project(
        jenkins_job=job,
        github_organisation='has-no-commits',
        github_repository='commit-less'
    )

    assert len(spy_calls) == 1
    assert spy_calls[0] == job


@pytest.mark.parametrize(
    "head, base, organisation, repository",
    [
        ('b', 'a', 'has-no-commits', 'commit-less'),
        ('c', 'd', 'another-org', 'commit-ful'),
    ]
)
def test_can_pass_parameters_to_get_commits_between_correctly(head, base, organisation, repository):
    builds = [
        Build(
            started_at=0,
            finished_at=1,
            successful=True,
            environment='Production',
            git_reference=base
        ),
        Build(
            started_at=0,
            finished_at=2,
            successful=True,
            environment='Production',
            git_reference=head
        )
    ]

    spy_calls = []

    def spy(**kwargs):
        spy_calls.append(kwargs)
        return []

    get_lead_time_for_project = GetLeadTimeForProject(
        get_commits_between=spy,
        get_jenkins_builds=lambda _: builds
    )
    get_lead_time_for_project(
        jenkins_job='a/job',
        github_organisation=organisation,
        github_repository=repository
    )

    assert len(spy_calls) == 1
    assert spy_calls[0]['head'] == head
    assert spy_calls[0]['base'] == base
    assert spy_calls[0]['organisation'] == organisation
    assert spy_calls[0]['repository'] == repository
