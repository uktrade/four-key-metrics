from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics, DataPresenter


def generate_lead_time_metrics(projects: dict, data_presenter: DataPresenter):
    return GenerateLeadTimeMetrics().generate_lead_time_metrics(
        projects, data_presenter
    )
