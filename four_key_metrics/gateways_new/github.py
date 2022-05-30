import os
import requests
import ciso8601

from four_key_metrics.domain_models import GitCommit


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