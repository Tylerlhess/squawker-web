test: ## Run tests
	echo "running tests"
	python -m pytest

echo:
	apt-get install python3 pip -y
	pip install -r requirements.txt
	python -m pytest