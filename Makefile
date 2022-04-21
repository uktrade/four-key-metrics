code-format:
	@echo "Black code formatting"	
	poetry run black {**/*.py,*.py}
