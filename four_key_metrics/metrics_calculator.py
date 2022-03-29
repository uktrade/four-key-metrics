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

    def add_deploy(self, timestamp, commit_timestamps, commit_hash):
        # print("COMIT_HASS:", commit_hash)
        if len(commit_timestamps) == 0:
            return

        self.deploys.append(
            {
                "timestamp": timestamp,
                "commit_timestamps": commit_timestamps,
                "commit_hash": commit_hash,
            }
        )

    def _get_lead_times(self):
        lead_times = []
        # pprint(self.deploys)
        for deploy in self.deploys:
            print(
                "COMMIT_HASH:",
                deploy["commit_hash"],
            )
            for commit_timestamp in deploy["commit_timestamps"]:
                lead_time = deploy["timestamp"] - commit_timestamp
                lead_times.append(lead_time)
                print(str(timedelta(seconds=lead_time)))
        # #            print(
        #  #               "deploy[timestamp]-commit",
        #    #             datetime.fromtimestamp(deploy["timestamp"]).strftime("%c"),
        #   #              datetime.fromtimestamp(commit_timestamp).strftime("%c"),
        #                 "lead_time",
        #                 str(timedelta(seconds=lead_time)),
        #             )
        # pprint(lead_times)
        #       print(
        ##            "deplo",
        #          datetime.fromtimestamp(deploy["timestamp"]).strftime("%c"),
        #            "lead times:",
        #            lead_times,
        #            len(lead_times),
        #            str(timedelta(seconds=sum(lead_times) / len(lead_times))),
        #     )
        print()
        return lead_times

    def _no_deploys(self) -> bool:
        return len(self.deploys) == 0
