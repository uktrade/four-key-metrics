GIT_PROJECTS = [
    {
        "job":"contact-form-production-deploy",
        "repository": "dit-contact-forms",
        "environment": "production",
    },
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
    {
        "job":"ess-production-deploy",
        "repository": "export-support",
        "environment": "production",
    },
    {
        "job":"helpdesk-production-deploy-public",
        "repository": "dit-helpdesk",
        "environment": "production",
    },
    {
        "job":"market-access-api-prod",
        "repository": "market-access-api",
        "environment": "production",
    },
    {
        "job":"market-access-fe-prod",
        "repository": "market-access-python-frontend",
        "environment": "production",
    },
    {
        "job":"market-access-public-fe-prod",
        "repository": "market-access-public-frontend",
        "environment": "production",
    },
    {
        "job":"update-supply-chain-information",
        "repository": "update-supply-chain-information",
        "environment": "production",
    }
]

PINGDOM_CHECK_NAMES = [
    "CHEG contact form",
    "Data Hub P1",
    "Data Hub P2",
    "Export Support Service",
    "Market Access API",
    "Market Access CITB",
    "Market Access FE",
    "Trade Helpdesk",
    "update-supply-chain-information",
]

JENKINS_JOBS = [
    "contact-form-production-deploy",
    "datahub-api",
    "datahub-fe",
    "ess-production-deploy",
    "helpdesk-production-deploy-public",
    "market-access-api-prod",
    "market-access-fe-prod",
    "market-access-public-fe-prod",
    "update-supply-chain-information",
]

CIRCLE_CI_PROJECTS = [
    {
        "project": "gh/uktrade/data-hub-api",
        "workflows": ["Default build"],
        "branches": ["main", "master"],
    },
    {
        "project": "gh/uktrade/data-hub-frontend",
        "workflows": ["datahub"],
        "branches": ["main", "master"],
    },
    {
        "project": "gh/uktrade/dit-contact-forms",
        "workflows": ["helpdesk"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/dit-helpdesk",
        "workflows": ["helpdesk"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/export-support",
        "workflows": ["export-support"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/market-access-api",
        "workflows": ["test"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/market-access-public-frontend",
        "workflows": ["test"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/market-access-python-frontend",
        "workflows": ["test"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/update-supply-chain-information",
        "workflows": ["workflow"],
        "branches": ["main"],
    }
]

GRAFANA_ALERTS = [
    {"name": "Database connection alert", "environment": "production"}
]
