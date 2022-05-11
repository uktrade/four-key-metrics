MTR_FIELD_NAMES = [
    "source",
    "project",
    "down_timestamp",
    "down_time",
    "up_timestamp",
    "up_time",
    "seconds_to_restore",
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
