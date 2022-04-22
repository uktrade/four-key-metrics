import os


def remove_generated_reports(extension=".csv"):
    for file in os.listdir("."):
        if file.endswith(extension):
            os.remove(file)
            print(os.path.join("Removed ./", file))
