GIT_PROJECTS = [
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
        "job":"contact-form-production-deploy",
        "repository": "dit-contact-forms",
        "environment": "production",
    },
    {
        "job":"ess-production-deploy",
        "repository": "export-support",
        "environment": "production",
    },
    {
        "job":"market-access-public-fe-prod",
        "repository": "market-access-public-frontend",
        "environment": "production",
    },
    {
        "job":"market-access-api-prod",
        "repository": "market-access-api",
        "environment": "production",
    }
]

PINGDOM_CHECK_NAMES = [
    "Data Hub P1",
    "Data Hub P2",
    "CHEG contact form",
    "Export Support Service",
    "Market Access CITB",
    "Market Access API",
]

JENKINS_JOBS = [
    "datahub-api",
    "datahub-fe",
    "contact-form-production-deploy",
    "ess-production-deploy",
    "market-access-public-fe-prod",
    "market-access-api-prod",
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
    {
        "project": "gh/uktrade/dit-contact-forms",
        "workflows": ["helpdesk"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/export-support",
        "workflows": ["export-support"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/market-access-public-frontend",
        "workflows": ["test"],
        "branches": ["master"],
    },
    {
        "project": "gh/uktrade/market-access-api",
        "workflows": ["test"],
        "branches": ["master"],
    },
]

GRAFANA_ALERTS = [
    {"name": "Database connection alert", "environment": "production"}
]

# Might need a service name mapping constant, as many awkward names exist for one product (like dit-helpdesk is actually TWUK)
SERVICE_NAME_MAPPING = {
    "contact-form-production-deploy": "CHEG Contact Forms",
    "gh/uktrade/dit-contact-forms": "CHEG Contact Forms",
    "CHEG contact form": "CHEG Contact Forms",
    "ess-production-deploy": "Export Support Service (ESS)",
    "export-support": "Export Support Service (ESS)",
    "gh/uktrade/export-support": "Export Support Service (ESS)",
    "gh/uktrade/market-access-public-frontend":"Check International Trade Barriers (CITB)",
    "market-access-public-fe-prod":"Check International Trade Barriers (CITB)",
    "Market Access CITB":"Check International Trade Barriers (CITB)",
    "market-access-public-frontend":"Check International Trade Barriers (CITB)",
    "gh/uktrade/market-access-api":"Market Access API",
    "market-access-api-prod":"Market Access API",
    "market-access-api":"Market Access API",
}
