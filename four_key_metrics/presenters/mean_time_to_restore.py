import csv
import json
import os
from datetime import timedelta, datetime
from pprint import pprint

from four_key_metrics.constants import MTR_FIELD_NAMES


class ConsolePresenter:
    def failure(self, source):
        pprint({"source": source, "average": None, "count": None})

    def success(self, source, mean_time_to_restore_average, outages_count):
        pprint(
            {
                "source": source,
                "average": mean_time_to_restore_average,
                "count": outages_count,
            },
            sort_dicts=False,
        )


class CSVDataPresenter(ConsolePresenter):
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self._file_name = file_name
        self._field_names = field_names

    @staticmethod
    def create():
        return CSVDataPresenter(
            f"mean_time_to_restore_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv",
            MTR_FIELD_NAMES,
        )

    def begin(self):
        self._csv_file = open(
            self._file_name,
            "w",
            newline="",
        )
        self._writer = csv.DictWriter(self._csv_file, fieldnames=self._field_names)
        self._writer.writeheader()

    def add(self, data: dict):
        self._writer.writerow(data)

    def end(self) -> list:
        self._csv_file.close()
        print("CSV metrics stored in", self._file_name)
