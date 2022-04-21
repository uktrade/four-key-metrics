code-format:
	@echo "Autopep8 flake8"
	autopep8 --in-place --aggressive ./four_key_metrics/*.py
	autopep8 --in-place --aggressive ./tests/*.py