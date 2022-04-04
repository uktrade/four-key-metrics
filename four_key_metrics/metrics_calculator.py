from datetime import timedelta, datetime
from pprint import pprint

import statistics


class MetricsCalculator(object):
    def __init__(self) -> None:
        self.deploys = []
        self.lead_times = []

    # Would live on AllBuilds class
    def get_lead_time_mean_average(self):
        if self._no_deploys():
            return None
        return sum(self.lead_times) / len(self.lead_times)

    # Would live on AllBuilds class
    def get_lead_time_standard_deviation(self):
        if self._no_deploys():
            return None
        return statistics.pstdev(self.lead_times)

    # Wouldn't be needed anymore
    def add_deploy(
        self, build_timestamp, commits, build_commit_hash, previous_build_commit_hash
    ):
        if len(commits) == 0:
            return

        self.deploys.append(
            {
                "commits": commits,
                "build_timestamp": build_timestamp,
                "build_commit_hash": build_commit_hash,
                "previous_build_commit_hash": previous_build_commit_hash,
            }
        )

    # Would live in Builds and get lead time for each commit populating GitCommit.lead_time
    def calculate_lead_times(self):
        for deploy in self.deploys:
            for commit in deploy["commits"]:
                commit.lead_time = deploy["build_timestamp"] - commit.timestamp
                self.lead_times.append(commit.lead_time)
        return None

    def _no_deploys(self) -> bool:
        return len(self.deploys) == 0
