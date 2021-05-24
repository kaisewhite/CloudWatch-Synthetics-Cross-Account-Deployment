# Define make entry and help functionality
.DEFAULT_GOAL := help

.PHONY: help

REPO_NAME := csbs-cdk-cw-syn
SHA1 := $$(git log -1 --pretty=%h)
CURRENT_BRANCH := $$(git symbolic-ref -q --short HEAD)
LATEST_TAG := ${REPO_NAME}:latest
GIT_TAG := ${REPO_NAME}:${SHA1}
VERSION := 0.1.0

info: ## Show information about the current git state.
	@echo "CodeCommit Project: codecommit://<aws_profile_to_mgmt>@${REPO_NAME}\nRepo Location: https://git-codecommit.us-east-1.amazonaws.com/v1/repos/${REPO_NAME}\nCurrent Branch: ${CURRENT_BRANCH}\nSHA1: ${SHA1}\n"

lint: isort ## Lint the NMLS Infra CDK project with Black.
	@poetry run black .

update-prereqs: ## Update the local development pre-requisite packages.
	@pip install --upgrade wheel setuptools pip

install-py-deps: update-prereqs ## Install the Python dependencies specified in the Pipfile.lock.
	@echo "Installing Python project dependencies..."
	@poetry install
	@echo "Python dependencies installed!"

init: ## Initialize the project.
	@pip install --upgrade wheel setuptools pip
	@curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
	@source $HOME/.poetry/env
	@poetry install

isort: ## Run isort against the project.
	@poetry run isort --profile black .

safety: ## Run the Python Safety dependency checker.
	@echo "Running Safety check..."
	@poetry run safety check
	@echo "Safety check completed!"

fix-eol: ## Fix bad cross-platform line ending characters that could result in python/r errors in terminal.
	@echo "Converting all python files to Unix..."
	@dos2unix app.py
	@dos2unix  modules/**/**/*.py
	@echo "Conversion completed!"

test: ## Run pytest unittests against the project.
	@echo "Running unit tests on changed files..."
	@poetry run python -m pytest --pick
	@echo "Partial unit testing completed!"

ci-test: ## Run pytest unittests against the project in CI.
	@echo "Running unit tests..."
	@poetry run python -m pytest .
	@echo "Unit testing completed!"

update-fork: ## Update the current fork master branch with upstream master.
	@echo "Updating the current fork with the upstream master branch..."
	@git checkout master
	@git fetch upstream
	@git merge upstream/master
	@git push origin master
	@echo "Updated!"

update-deps: update-prereqs ## Update the package dependencies via poetry.
	@poetry update

install: isort ## Install the local development version of the module.
	@poetry install .

help: ## Show this help information.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-25s\033[0m %s\n", $$1, $$2}'
