from cmd import Cmd
from pprint import pprint

from dotenv import load_dotenv

from four_key_metrics.constants import (
    CIRCLE_CI_PROJECTS,
    GIT_PROJECTS,
    GRAFANA_ALERTS,
    JENKINS_JOBS,
    PINGDOM_CHECK_NAMES,
)
from four_key_metrics.utilities import remove_generated_reports
from four_key_metrics.presenters.lead_time_metrics import (
    CSVDataPresenter as LeadTimeCSVDataPresenter,
    JSONDataPresenter,
)
from four_key_metrics.presenters.mean_time_to_restore import (
    CSVDataPresenter as MeanTimeCSVDataPresenter,
)
from four_key_metrics.use_case_factory import UseCaseFactory

load_dotenv()


class DisplayShell(Cmd):
    """Command allowing specific reports to be generated through actions"""

    intro = "Welcome to the key metrics shell. Type help or ?.\n"
    prompt = "(type <topic> to generate report) "

    def do_ltm(self, arg):
        """Generate lead time time metrics

        Args:
            arg (string): outsput type defaulting to 'csv' but accepting
            'json'
        """
        self.do_lead_time_metrics(arg)

    def do_lead_time_metrics(self, arg):
        """Generate lead time time metrics

        Args:
            arg (string): output type defaulting to 'csv' but accepting
            'json',
        """
        # TODO: Make this easier to pass and parse these values through the command line
        projects = GIT_PROJECTS
        default_output = LeadTimeCSVDataPresenter()
        data_presenter = {
            "": default_output,
            "csv": default_output,
            "json": JSONDataPresenter(),
        }[arg.lower()]
        UseCaseFactory().create("generate_lead_time_metrics")(projects, data_presenter)

    def do_mtr(self, args):
        """Generate mean time to restore metric"""

        self.do_mean_time_to_restore(args)

    def do_mean_time_to_restore(self, args):
        """Generate mean time to restore metric"""

        pingdom_check_names = PINGDOM_CHECK_NAMES
        jenkins_jobs = JENKINS_JOBS
        circle_ci_projects = CIRCLE_CI_PROJECTS
        grafana_alert_names = GRAFANA_ALERTS

        UseCaseFactory().create("generate_mean_time_to_restore")(
            pingdom_check_names,
            jenkins_jobs,
            circle_ci_projects,
            grafana_alert_names,
            MeanTimeCSVDataPresenter.create(),
        )

    def do_4km(self, args):
        """Generate four key metrics
        (currently Lead Time Metrics and Mean Time To Restore only)"""

        self.do_four_key_metrics(args)

    def do_four_key_metrics(self, args):
        """Generate four key metrics
        (currently Lead Time Metrics and Mean Time To Restore only)"""

        self.do_lead_time_metrics(args)
        self.do_mean_time_to_restore(args)

    def do_remove_reports(self, arg):
        """Clean up generated reports by supported output types, e.g. .csv

        Args:
            arg (string): Defaults to '.csv' but can be overriden to support
                '.json, '.txt', '.xml' or other supported types
        """
        fileExtension = ".csv"
        if arg:
            fileExtension = arg
        pprint(f"searching {fileExtension}")
        remove_generated_reports(fileExtension)

    def do_close(self, line):
        """Close or exit application"""
        return True


if __name__ == "__main__":

    DisplayShell().cmdloop()
