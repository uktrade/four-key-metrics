from typing import List, Protocol
from four_key_metrics.gateways import PingdomErrors


class GenerateMeanTimeToRestorePresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def failure(self, pingdom_check_names):
        ...

    def success(
        self,
        source,
        mean_time_to_restore_average,
    ):
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
        all_errors = PingdomErrors().get_pingdom_errors(check_names)
        total_time_to_restore = 0
        for e in all_errors:
            total_time_to_restore += e.seconds_to_restore
        mean_time_to_restore = total_time_to_restore / len(all_errors)
        self._presenter.success("pingdom", mean_time_to_restore)
        return int(mean_time_to_restore)
