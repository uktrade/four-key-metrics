# Four Key Metrics

[![CircleCI](https://circleci.com/gh/uktrade/four-key-metrics/tree/main.svg?style=svg)](https://circleci.com/gh/uktrade/four-key-metrics/tree/main)

Intended as a way to measure the `four key metrics` as defined in the book Accelerate by Forsgren, Humble and Kim.

- [X] [product delivery] lead time (Time between code committed and code deployed)
- [ ] deployment frequency (Number of deployments of new code per day)
- [ ] mean time to restore (MTTR) (How long does it take to restore the service after it has been impaired?)
- [ ] change fail percentage (% of times the CI/CD pipeline for the default branch fails or causes an outage in any environment)

## Local setup

pre-requisites: 
- poetry

`poetry install`


## Testing

`poetry run pytest`

## Running the tool

In order to run the tool you need to set these environment variables

```bash
export GITHUB_USERNAME='my-username'
export GITHUB_TOKEN='1234'
export DIT_JENKINS_USER='a-username'
export DIT_JENKINS_TOKEN='5678'
```

`poetry run python display.py`

