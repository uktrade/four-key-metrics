import os
import re


def get_filename_and_captured_outerr(capsys, prefix, filetype):
    captured = capsys.readouterr()
    regex_filename = prefix + "[0-9]{2}-[0-9]{2}-[0-9]{4}_[0-9]{6}." + filetype
    filename = re.search(regex_filename, captured.out).group()
    return filename, captured


def clean_up_csv_file(csv_filename):
    file_exists = os.path.exists(csv_filename)
    if file_exists:
        os.remove(csv_filename)
