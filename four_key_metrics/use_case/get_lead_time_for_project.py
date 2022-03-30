from four_key_metrics.metrics_calculator import MetricsCalculator


class GetLeadTimeForProject(object):
    def __init__(self, get_commits_between, get_jenkins_builds):
        self.get_jenkins_builds = get_jenkins_builds
        self.get_commits_between = get_commits_between

    def __call__(
        self, jenkins_job, github_organisation, github_repository, environment
    ):
        jenkins_builds = self._get_jenkins_builds(jenkins_job, environment)
        jenkins_builds.sort(key=lambda b: b.finished_at)
        if len(jenkins_builds) < 2:
            return {
                "successful": False,
                "lead_time_mean_average": None,
                "lead_time_standard_deviation": None,
            }

        calculator = MetricsCalculator()
        last_build = jenkins_builds.pop(0)
        for build in jenkins_builds:
            # TODO get list of build hashes to ignore from env file
            if build.git_reference != "53857a55457f6d65be43aa022326289be0cf3f74":
                commits = self.get_commits_between(
                    organisation=github_organisation,
                    repository=github_repository,
                    base=last_build.git_reference,
                    head=build.git_reference,
                )
                calculator.add_deploy(
                    build_timestamp=build.finished_at,
                    commits=commits,
                    build_commit_hash=build.git_reference,
                    previous_build_commit_hash=last_build.git_reference,
                )
            last_build = build
        calculator.calculate_lead_times()
        return {
            "successful": True,
            "lead_time_mean_average": calculator.get_lead_time_mean_average(),
            "lead_time_standard_deviation": calculator.get_lead_time_standard_deviation(),
            "deploys": calculator.deploys,
        }

    def _get_jenkins_builds(self, jenkins_job, environment):
        jenkins_builds = self.get_jenkins_builds(jenkins_job)
        return list(filter(lambda b: b.environment == environment, jenkins_builds))
