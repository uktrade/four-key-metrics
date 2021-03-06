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


class Outage:
    def __init__(
        self,
        source,
        project,
        environment,
        down_timestamp,
        up_timestamp,
        pingdom_check_id=None,
        jenkins_failed_build_hash=None,
        circle_ci_failed_run_id=None,
        grafana_alert_name=None,
    ):
        self.source = source
        self.project = project
        self.environment = environment
        self.pingdom_check_id = pingdom_check_id or None
        self.down_timestamp = down_timestamp
        self.up_timestamp = up_timestamp
        self.seconds_to_restore = self.up_timestamp - self.down_timestamp
        self.jenkins_failed_build_hash = jenkins_failed_build_hash or None
        self.circle_ci_failed_run_id = circle_ci_failed_run_id or None
        self.grafana_alert_name = grafana_alert_name or None