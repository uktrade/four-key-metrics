import os

from display import remove_generated_reports


def test_generated_reports_get_removed():
    with open("test.txt", "w") as test_file:
        test_file.write("Generated metrics test cleanup")
        assert os.path.exists("test.txt") is True

    remove_generated_reports(".txt")

    assert os.path.exists("test.txt") is False
