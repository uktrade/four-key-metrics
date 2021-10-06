import statistics


class MetricsCalculator(object):
    def __init__(self) -> None:
        self.deploys = []

    def get_lead_time_mean_average(self):
        if self._no_deploys():
            return None

        lead_times = self._get_lead_times()
        return sum(lead_times) / len(lead_times)

    def get_lead_time_standard_deviation(self):
        if self._no_deploys():
            return None

        return statistics.pstdev(self._get_lead_times())

    def add_deploy(self, timestamp, commit_timestamps):
        self.deploys.append({
            "timestamp": timestamp,
            "commit_timestamps": commit_timestamps,
        })

    def _get_lead_times(self):
        lead_times = []
        for deploy in self.deploys:
            for commit_timestamp in deploy['commit_timestamps']:
                lead_times.append(deploy['timestamp'] - commit_timestamp)
        return lead_times

    def _no_deploys(self) -> bool:
        return len(self.deploys) == 0
