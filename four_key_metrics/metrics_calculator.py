from datetime import timedelta, datetime
from pprint import pprint

import statistics


class MetricsCalculator(object):
    def __init__(self) -> None:
        self.deploys = []

    def get_lead_time_mean_average(self):
        if self._no_deploys():
            return None
        print("get_lead_time_mean_average")
        lead_times = self._get_lead_times()

        return sum(lead_times) / len(lead_times)

    def get_lead_time_standard_deviation(self):
        if self._no_deploys():
            return None
        print("get_lead_time_standard_deviation")
        return statistics.pstdev(self._get_lead_times())

    def add_deploy(self, timestamp, commits, commit_timestamps, commit_hash):
        if len(commit_timestamps) == 0:
            return

        self.deploys.append(
            {
                "commits": commits,
                "timestamp": timestamp,
                "commit_timestamps": commit_timestamps,
                "commit_hash": commit_hash,
            }
        )

    def _get_lead_times(self):
        lead_times = []
        # pprint(self.deploys)
        for deploy in self.deploys:
            for commit in deploy["commits"]:
                lead_time = deploy["timestamp"] - commit.timestamp
                if deploy["commit_hash"] != "53857a55457f6d65be43aa022326289be0cf3f74":
                    lead_times.append(lead_time)
                if timedelta(seconds=lead_time) > timedelta(days=200):
                    print(
                        "DEPLOYMENT COMMIT_HASH: ",
                        deploy["commit_hash"],
                        "DEPLOYMENT TIME: ",
                        datetime.fromtimestamp(deploy["timestamp"]).strftime("%c"),
                    )
                    print(
                        "COMMIT HASH",
                        commit.sha,
                        "COMMIT TIME",
                        datetime.fromtimestamp(commit.timestamp).strftime("%c"),
                        "LEAD TIME",
                        str(timedelta(seconds=lead_time)),
                    )
                    print("")
        return lead_times

    def _no_deploys(self) -> bool:
        return len(self.deploys) == 0
