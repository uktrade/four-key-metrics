import csv
import json
import os
from datetime import timedelta, datetime
from pprint import pprint

LTM_FIELD_NAMES = [
    "repository",
    "build_commit_hash",
    "build_timestamp",
    "build_time",
    "commit_hash",
    "commit_timestamp",
    "commit_time",
    "commit_lead_time_days",
    "commit_lead_time",
    "previous_build_commit_hash",
]


class ConsolePresenter:
    def failure(self, project):
        pprint(
            {
                "project": project,
                "average": None,
                "standard_deviation": None,
            }
        )

    def success(
        self,
        repository,
        environment,
        lead_time_mean_average,
        lead_time_standard_deviation,
    ):
        pprint(
            {
                "project": repository,
                "environment": environment,
                "average": str(timedelta(seconds=lead_time_mean_average)),
                "standard_deviation": str(
                    timedelta(seconds=lead_time_standard_deviation)
                ),
            },
            sort_dicts=False,
        )


def _to_output_dict(data):
    return {
        "repository": data["repository"],
        "build_commit_hash": data["build_commit_hash"],
        "build_timestamp": data["build_timestamp"],
        "build_time": datetime.fromtimestamp(data["build_timestamp"]).strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "commit_hash": data["commit_hash"],
        "commit_timestamp": data["commit_timestamp"],
        "commit_time": datetime.fromtimestamp(data["commit_timestamp"]).strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "commit_lead_time_days": data["commit_lead_time"] / 86400,
        "commit_lead_time": str(timedelta(seconds=data["commit_lead_time"])),
        "previous_build_commit_hash": data["previous_build_commit_hash"],
    }


class CSVDataPresenter(ConsolePresenter):
    def __init__(self) -> None:
        self._file_name = (
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.csv"
        )
        self._field_names = LTM_FIELD_NAMES

    def begin(self):
        self._csv_file = open(
            self._file_name,
            "w",
            newline="",
        )
        self._writer = csv.DictWriter(self._csv_file, fieldnames=self._field_names)
        self._writer.writeheader()

    def add(self, data: dict):
        self._writer.writerow(_to_output_dict(data))

    def end(self):
        self._csv_file.close()
        print("CSV metrics stored in", self._file_name)


class JSONDataPresenter(ConsolePresenter):
    def __init__(self) -> None:
        self._file_name = (
            f"lead_time_metrics_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.json"
        )
        self._field_names = LTM_FIELD_NAMES

    def begin(self):
        self._json_file = open(self._file_name, "w")
        self._has_data = False

    def add(self, data: dict):
        json_data = json.dumps(_to_output_dict(data), sort_keys=True, indent=2)
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
