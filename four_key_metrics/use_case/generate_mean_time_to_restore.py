from datetime import datetime
from typing import List, Protocol
from four_key_metrics.gateways import PingdomOutages


class GenerateMeanTimeToRestorePresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def failure(self, pingdom_check_names):
        ...

    def success(self, source, mean_time_to_restore_average, outages_count):
        ...


class GenerateMeanTimeToRestore:
    def __init__(self):
        return

    def __call__(
        self, pingdom_check_names, presenter: GenerateMeanTimeToRestorePresenter
    ):
        self._presenter = presenter
        try:
            self._presenter.begin()
            self._get_pingdom_mean_time_to_restore(pingdom_check_names)
        finally:
            self._presenter.end()

    def _get_pingdom_mean_time_to_restore(self, check_names: List[str]):
        all_outages = PingdomOutages().get_pingdom_outages(check_names)
        total_time_to_restore = 0
        for outage in all_outages:
            total_time_to_restore += outage.seconds_to_restore
            self._presenter.add(
                {
                    "source": "pingdom",
                    "project": outage.check_name,
                    "down_timestamp": outage.down_timestamp,
                    "down_time": datetime.fromtimestamp(outage.down_timestamp).strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "up_timestamp": outage.up_timestamp,
                    "up_time": datetime.fromtimestamp(outage.up_timestamp).strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "seconds_to_restore": outage.seconds_to_restore,
                }
            )

        if not all_outages:
            self._presenter.failure("pingdom")
            return None

        mean_time_to_restore = total_time_to_restore / len(all_outages)
        self._presenter.success("pingdom", mean_time_to_restore, len(all_outages))
        return int(mean_time_to_restore)
