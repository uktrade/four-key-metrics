# Four Key Metrics

[![CircleCI](https://circleci.com/gh/uktrade/four-key-metrics/tree/main.svg?style=svg)](https://circleci.com/gh/uktrade/four-key-metrics/tree/main)

Intended as a way to measure the `four key metrics` as defined in the book Accelerate by Forsgren, Humble and Kim.

- [x] [product delivery] lead time (Time between code committed and code deployed)
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

In order to run the tool you need to **copy the sample.env** to .env and configure the following environment variables:

```bash
export GITHUB_USERNAME='my-username'
export GITHUB_TOKEN='1234'
export DIT_JENKINS_USER='a-username'
export DIT_JENKINS_TOKEN='5678'
```

`poetry run python display.py`

Note on tests not appearing in vscode
A common reason for this is that you're trying to run tests with dependencies. If this is the case, you can select your interpreter by running ctrl/cmd + shift + p and searching Python: Select Interpreter, then selecting the correct interpreter.

## Data structure

Jenkins returns a list of all builds for a project. The list of builds is checked against GitHub commits to calculate lead times.
