from four_key_metrics.metrics_calculator import MetricsCalculator


def test_can_calculate_metrics_for_nothing():
    calculator = MetricsCalculator()
    assert calculator.get_lead_time_mean_average() is None
    assert calculator.get_lead_time_standard_deviation() is None


def test_can_calculate_metrics_for_single_deploy_with_no_commits():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=1, commit_timestamps=[])

    assert calculator.get_lead_time_mean_average() is None
    assert calculator.get_lead_time_standard_deviation() is None


def test_can_calculate_metrics_for_one_deploy_with_one_commit():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=1, commit_timestamps=[0])

    assert calculator.get_lead_time_mean_average() == 1
    assert calculator.get_lead_time_standard_deviation() == 0


def test_can_calculate_metrics_for_one_deploy_with_two_commits():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=10, commit_timestamps=[8, 8])

    assert calculator.get_lead_time_mean_average() == 2
    assert calculator.get_lead_time_standard_deviation() == 0


def test_can_calculate_metrics_for_two_deploys_with_two_commits():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=10, commit_timestamps=[8, 8])
    calculator.add_deploy(timestamp=20, commit_timestamps=[9, 9])

    assert calculator.get_lead_time_mean_average() == 6.5
    assert calculator.get_lead_time_standard_deviation() == 4.5
