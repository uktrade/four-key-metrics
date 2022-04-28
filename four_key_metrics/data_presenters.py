import csv
import json
import os
from datetime import datetime
from typing import Protocol

from four_key_metrics.constants import LTM_FIELD_NAMES


class DataPresenter(Protocol):
    def add(self, data: dict):
        ...

    def begin(self):
        ...

    def end(self):
        ...


class CSVDataPresenter:
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self.file_name = file_name
        self.field_names = field_names

    @staticmethod
    def create():
        return CSVDataPresenter(
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv",
            LTM_FIELD_NAMES
        )

    def begin(self):
        self.csv_file = open(
            self.file_name,
            "w",
            newline="",
        )
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.field_names)
        self.writer.writeheader()

    def add(self, data: dict):
        self.writer.writerow(data)

    def end(self) -> list:
        self.csv_file.close()
        print("CSV metrics stored in", self.file_name)


class JSONDataPresenter:
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self.file_name = file_name
        self.field_names = field_names

    @staticmethod
    def create():
        return JSONDataPresenter(
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.json",
            LTM_FIELD_NAMES
        )

    def begin(self):
        self.json_file = open(self.file_name, "w")
        self._has_data = False

    def add(self, data: dict):
        json_data = json.dumps(data, sort_keys=True, indent=2)
        if self._has_data is False:
            self.json_file.write(f"[{json_data}")
        else:
            self.json_file.write(f",{os.linesep}{json_data}")
        self._has_data = True

    def end(self):
        self.json_file.write("]")
        self.json_file.close()
        print("JSON metrics stored in", self.file_name)
