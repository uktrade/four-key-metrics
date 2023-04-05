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
    }
]

PINGDOM_CHECK_NAMES = [
    "Data Hub P1",
    "Data Hub P2",
    "CHEG contact form",
]

JENKINS_JOBS = [
    "datahub-api",
    "datahub-fe",
    "contact-form-production-deploy",
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
]

GRAFANA_ALERTS = [
    {"name": "Database connection alert", "environment": "production"}
]

# Might need a service name mapping constant, as many awkward names exist for one product (like dit-helpdesk is actually TWUK)
SERVICE_NAME_MAPPING = {
    "contact-form-production-deploy":"cheg-contact-forms",
    "gh/uktrade/dit-contact-forms":"cheg-contact-forms",
    "CHEG contact form":"cheg-contact-forms",
}
