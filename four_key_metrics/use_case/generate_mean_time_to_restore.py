from typing import List
from four_key_metrics.gateways import PingdomErrors


def get_pingdom_mean_time_to_restore(check_names: List[str]) -> float:
    all_errors = PingdomErrors().get_pingdom_errors(check_names)
    total_time_to_restore = 0
    for e in all_errors:
        total_time_to_restore += e.seconds_to_restore
    return total_time_to_restore / len(all_errors)
