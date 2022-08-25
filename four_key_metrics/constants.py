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
    "Data Hub P1",
    "Data Hub P2",
]

JENKINS_JOBS = [
    "datahub-api",
    "datahub-fe",
]

CIRCLE_CI_PROJECTS = [
    {
        "project": "gh/uktrade/data-hub-frontend",
        "workflows": ["datahub"],
        "branches": ["main", "master"],
    },
    {
        "project": "gh/uktrade/data-hub-api",
        "workflows": ["Default build"],
        "branches": ["main", "master"],
    },
]

GRAFANA_ALERTS = [{"name": "Database connection alert", "environment": "production"}]
