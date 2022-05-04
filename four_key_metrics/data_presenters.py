import csv
import json
import os
from datetime import datetime
from pprint import pprint
from typing import Protocol

from four_key_metrics.constants import LTM_FIELD_NAMES


class DataPresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def failure(self, project):
        ...

class ConsolePresenter:
    def failure(self, project):
        pprint(
            {
                "project": project,
                "average": None,
                "standard_deviation": None,
            }
        )


class CSVDataPresenter(ConsolePresenter):
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self._file_name = file_name
        self._field_names = field_names

    @staticmethod
    def create():
        return CSVDataPresenter(
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv",
            LTM_FIELD_NAMES,
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


class JSONDataPresenter(ConsolePresenter):
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self._file_name = file_name
        self._field_names = field_names

    @staticmethod
    def create():
        return JSONDataPresenter(
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.json",
            LTM_FIELD_NAMES,
        )

    def begin(self):
        self._json_file = open(self._file_name, "w")
        self._has_data = False

    def add(self, data: dict):
        json_data = json.dumps(data, sort_keys=True, indent=2)
        self._json_file.write(f"{self._delimiter()}{json_data}")
        self._has_data = True

    def end(self):
        self._json_file.write("]")
        self._json_file.close()
        print("JSON metrics stored in", self._file_name)

    def _delimiter(self):
        beginning_of_file = not self._has_data
        if beginning_of_file:
            return f"["

        return f",{os.linesep}"
