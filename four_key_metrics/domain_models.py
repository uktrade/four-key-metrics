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

    def set_last_build_git_reference(self, last_build_git_reference):
        self.last_build_git_reference = last_build_git_reference


class GitCommit:
    def __init__(self, sha, timestamp):
        self.sha = sha
        self.timestamp = timestamp