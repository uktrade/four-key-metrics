class MetricsCalculator(object):
    def __init__(self) -> None:
        self.deploys = []

    def average_lead_time(self):
        if len(self.deploys) == 0:
            return None

        lead_times = []

        for deploy in self.deploys:
            for commit_timestamp in deploy['commit_timestamps']:
                lead_times.append(deploy['timestamp'] - commit_timestamp)

        return sum(lead_times) / len(lead_times)

    def add_deploy(self, timestamp, commit_timestamps):
        self.deploys.append({
            "timestamp": timestamp,
            "commit_timestamps": commit_timestamps,
        })