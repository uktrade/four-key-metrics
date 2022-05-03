from four_key_metrics.data_presenters import (
    DataPresenter,
)
from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics


def generate_lead_time_metrics(projects: dict, data_presenter: DataPresenter):
    return GenerateLeadTimeMetrics().generate_lead_time_metrics(
        projects, data_presenter
    )
