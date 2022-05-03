LTM_FIELD_NAMES = [
    "repository",
    "build_commit_hash",
    "build_timestamp",
    "build_time",
    "commit_hash",
    "commit_timestamp",
    "commit_time",
    "commit_lead_time_days",
    "commit_lead_time",
    "previous_build_commit_hash",
]

DATAHUB_GIT_PROJECTS = [
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

PINGDOM_CHECK_NAMES = [
    "uk.gov.trade.datahub.api",
    "Data Hub P1",
    "Data Hub P2",
]

