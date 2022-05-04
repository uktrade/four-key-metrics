import os
import ciso8601
import requests

class GitHubCommits:
    def get_commits_between(self, organisation, repository, base, head):
        response = requests.get(
            "https://api.github.com/repos/%s/%s/compare/%s...%s?per_page=10000"
            % (organisation, repository, base, head),
            auth=(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_TOKEN"]),
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=30,
        )

        commits = []
        for commit in response.json()["commits"]:
            commit_author_date = commit["commit"]["author"]["date"]
            timestamp = ciso8601.parse_datetime(commit_author_date).timestamp()
            commits.append(GitCommit(sha=commit["sha"], timestamp=timestamp))
        return commits


class Build:
    def __init__(
        self,
        started_at,
        finished_at,
        successful,
        environment,
        git_reference,
    ):
        self.commits = []
        self.started_at = started_at
        self.finished_at = finished_at
        self.successful = successful
        self.environment = environment
        self.git_reference = git_reference
        self.last_build_git_reference = None

    def get_commits_between(self, organisation, repository, base, head):
        self.commits = GitHubCommits()\
            .get_commits_between(organisation, repository, base, head)
        return self.commits

    def set_last_build_git_reference(self, last_build_git_reference):
        self.last_build_git_reference = last_build_git_reference


class GitCommit:
    def __init__(self, sha, timestamp):
        self.sha = sha
        self.timestamp = timestamp