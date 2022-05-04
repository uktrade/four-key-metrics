from four_key_metrics.use_case.generate_lead_time_metrics import GenerateLeadTimeMetrics


class UseCaseFactory:
    def create(self, name):
        use_cases = {
            'generate_lead_time_metrics': GenerateLeadTimeMetrics()
        }
        return use_cases[name]
