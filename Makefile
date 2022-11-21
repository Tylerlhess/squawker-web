test: ## Run tests
	echo "running tests"
	python -m pytest

echo:
	apt-get install python -y
	python -m pytest