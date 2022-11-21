test: ## Run tests
	echo "running tests"
	python -m pytest

echo:
	apt-get install python3.9.4 -y
	pip install pytest
	python -m pytest