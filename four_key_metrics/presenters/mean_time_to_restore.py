import csv
from datetime import datetime
from pprint import pprint

MTR_FIELD_NAMES = [
    "source",
    "project",
    "down_timestamp",
    "down_time",
    "up_timestamp",
    "up_time",
    "seconds_to_restore",
]


class ConsolePresenter:
    def failure(self, source):
        pprint(
            {"source": source, "mean time to restore in seconds": None, "count": None}
        )

    def success(self, source, mean_time_to_restore_average, outages_count):
        pprint(
            {
                "source": source,
                "mean time to restore in seconds": mean_time_to_restore_average,
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
