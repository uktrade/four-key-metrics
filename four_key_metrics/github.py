import os

import ciso8601
import requests


class GitCommit:
    def __init__(self, sha, timestamp):
        self.sha = sha
        self.timestamp = timestamp
        self.lead_time = None


# Move to Build class
def get_commits_between(organisation, repository, base, head):
    response = requests.get(
        "https://api.github.com/repos/%s/%s/compare/%s...%s"
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
