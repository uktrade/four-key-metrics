format-code:
	@echo "Black code formatting for all python files in the project"	
	poetry run black {**/*.py,*.py}

metrics:
	poetry run python display.py

install:
	@echo "Install all the python libraries ready to run the application"	
	poetry install

test:
	@echo "Run tests"	
	poetry run pytest

watch-test:
	@make test --silent || exit 0
	@poetry run watchmedo shell-command --patterns="*.py" --recursive --drop --command="make test --silent" .
