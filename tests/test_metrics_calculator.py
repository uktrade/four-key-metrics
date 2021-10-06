from four_key_metrics.metrics_calculator import MetricsCalculator


def test_can_calculate_lead_time_for_nothing():
    assert MetricsCalculator().average_lead_time() is None


def test_can_calculate_lead_time_for_one_deploy_with_one_commit():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=1, commit_timestamps=[0])

    assert calculator.average_lead_time() == 1


def test_can_calculate_lead_time_for_one_deploy_with_two_commits():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=10, commit_timestamps=[8, 8])

    assert calculator.average_lead_time() == 2


def test_can_calculate_lead_time_for_two_deploys_with_two_commits():
    calculator = MetricsCalculator()

    calculator.add_deploy(timestamp=10, commit_timestamps=[8, 8])
    calculator.add_deploy(timestamp=20, commit_timestamps=[9, 9])

    assert calculator.average_lead_time() == 6.5
