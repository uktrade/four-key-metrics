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


class PingdomError:
    def __init__(self, check_name, check_id, down_timestamp, up_timestamp):
        self.check_name = check_name
        self.check_id = check_id
        self.down_timestamp = down_timestamp
        self.up_timestamp = up_timestamp
        self.seconds_to_restore = self.up_timestamp - self.down_timestamp
