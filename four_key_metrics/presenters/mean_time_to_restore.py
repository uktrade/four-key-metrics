import csv
import json
import os
from datetime import timedelta, datetime
from pprint import pprint

from four_key_metrics.constants import MTR_FIELD_NAMES


class ConsolePresenter:
    def failure(self, source):
        pprint(
            {
                "source": source,
                "average": None,
            }
        )

    def success(
        self,
        source,
        mean_time_to_restore_average,
    ):
        pprint(
            {
                "source": source,
                "average": mean_time_to_restore_average,
            },
            sort_dicts=False,
        )
