args ?= -vvv --cov replace_with_new_name
test: ## Run tests
    echo "running tests"
	pytest $(args)
