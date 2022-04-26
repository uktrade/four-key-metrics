import csv
from datetime import datetime
import json
import os

from four_key_metrics.constants import LTM_FIELD_NAMES


class DataPresenter:
    def __init__(self, file_name: str, field_names: list[str]) -> None:
        self.file_name = file_name
        self.field_names = field_names
        self.data_list = []

    @staticmethod
    def create(
        file_name=f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.txt",
        field_names=LTM_FIELD_NAMES,
    ):
        return DataPresenter(file_name=file_name, field_names=field_names)

    def add(self, data: dict):
        self.data_list.append(data)

    def begin(self):
        self.data_list = []

    def end(self):
        return self.data_list


class CSVDataPresenter(DataPresenter):
    def __init__(self, file_name: str, field_names: list[str]):
        super().__init__(file_name, field_names)

    @staticmethod
    def create(
        file_name=f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv",
        field_names=LTM_FIELD_NAMES,
    ):
        return CSVDataPresenter(file_name=file_name, field_names=field_names)

    def begin(self):
        self.csv_file = open(
            self.file_name,
            "w",
            newline="",
        )
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.field_names)
        self.writer.writeheader()
        super().begin()

    def add(self, data: dict):
        self.writer.writerow(data)
        super().add(data)

    def end(self) -> list:
        self.csv_file.close()
        print("CSV metrics stored in", self.file_name)
        return super().end()


class JSONDataPresenter(DataPresenter):
    def __init__(self, file_name: str, field_names: list[str]):
        super().__init__(file_name, field_names)

    @staticmethod
    def create(
        file_name=f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.json",
        field_names=LTM_FIELD_NAMES,
    ):
        if field_names is None:
            field_names = LTM_FIELD_NAMES
        return JSONDataPresenter(file_name=file_name, field_names=field_names)

    def begin(self):
        self.json_file = open(self.file_name, "w")
        self.has_data = False

    def add(self, data: dict):
        jsonData = json.dumps(data, sort_keys=True, indent=2)
        if self.has_data is False:
            self.json_file.write(f"[{jsonData}")
        else:
            self.json_file.write(f",{os.linesep}{jsonData}")
        self.has_data = True

    def end(self):
        self.json_file.write("]")
        self.json_file.close()
        print("JSON metrics stored in", self.file_name)
