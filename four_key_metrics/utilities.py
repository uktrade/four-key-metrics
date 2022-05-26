import os
from datetime import datetime

def remove_generated_reports(extension=".csv"):
    for file in os.listdir("."):
        if file.endswith(extension):
            os.remove(file)
            print(os.path.join("Removed ./", file))

def iso_string_to_timestamp(iso_string):
    iso_string_datetime=(datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ"))
    time_stamp =datetime.timestamp(iso_string_datetime)
    return time_stamp