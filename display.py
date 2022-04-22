from cmd import Cmd
from pprint import pprint
from dotenv import load_dotenv

from four_key_metrics.file_utilities import remove_generated_reports
from four_key_metrics.lead_time_metrics import generate_lead_time_metrics

load_dotenv()


class DisplayShell(Cmd):
    """Command allowing specific reports to be generated through actions"""

    intro = "Welcome to the key metrics shell. Type help or ?.\n"
    prompt = "(type <topic> to generate report) "

    def do_ltm(self, arg):
        """Generate lead time time metrics

        Args:
            arg (json): TODO: Figure out what can be passed to make this more
            configurable
        """
        self.do_lead_time_metrics(arg)

    def do_lead_time_metrics(self, arg):
        """Generate lead time time metrics

        Args:
            arg (json): TODO: Figure out what can be passed to make this more
            configurable
        """
        projects = [
            {
                "job": "datahub-api",
                "repository": "data-hub-api",
                "environment": "production",
            },
            {
                "job": "datahub-fe",
                "repository": "data-hub-frontend",
                "environment": "production",
            },
        ]
        generate_lead_time_metrics(projects)

    def do_remove_reports(self, arg):
        """Clean up generated reports by supported output types, e.g. .csv

        Args:
            arg (string): Defaults to '.csv' but can be overriden to support
                '.json, '.txt', '.xml' or other supported types
        """
        fileExtension = ".csv"
        if arg:
            fileExtension = arg
        pprint("searching ", fileExtension)
        remove_generated_reports(fileExtension)


if __name__ == "__main__":

    DisplayShell().cmdloop()
