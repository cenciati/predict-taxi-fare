SHELL = /bin/bash
PYTHON := python3 -m
POETRY := poetry run

SOURCE_CODE_DIR := src/
TESTS_DIR := src/__tests__/
DOCKER_TAG_DEV_ENV := dev-env-nyc-taxis:latest


.PHONY: help
help: ## Display commands help screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
.PHONY: setup_db
setup_db: ## Set up only the database container
	docker-compose -f .docker/docker-compose.yaml --env-file .env up -d --build db

.PHONY: setup_dev_environment
.ONESHELL:
setup_dev_environment: ## Set up only the dev environment (jupyter, dev dependencies, etc.)
	docker build -t ${DOCKER_TAG_DEV_ENV} --target development -f .docker/Dockerfile .
	docker container run \
	-p 8888:8888 \
	-p 5000:5000 \
	--mount type=bind,source="$(pwd)",target=/home/jovyan/ \
	-d ${DOCKER_TAG_DEV_ENV}

.PHONY: prefect_deploy_and_run
.ONESHELL:
prefect_deploy_and_run_flow: ## Create a prefect flow deployment and run it right away
	python -m src.pipeline.batch_workflow -d ./data/raw/test/workflow_test_data.parquet

.PHONY: lint
lint: ## Run all linters and formatters
	${POETRY} ${PYTHON} isort ${SOURCE_CODE_DIR}
	${POETRY} ${PYTHON} black ${SOURCE_CODE_DIR}
	${POETRY} ${PYTHON} pylint ${SOURCE_CODE_DIR}

.PHONY: test
test: ## Run all tests
	${POETRY} ${PYTHON} pytest ${TESTS_DIR}

test_unit: ## Run only unit tests
	${POETRY} ${PYTHON} pytest ${TESTS_DIR} -k "unit"

test_integration: ## Run integration tests
	${POETRY} ${PYTHON} pytest ${TESTS_DIR} -k "integration"

test_e2e: ## Run end-to-end tests
	${POETRY} ${PYTHON} pytest ${TESTS_DIR} -k "e2e"

.PHONY: run_api_locally
run_api_locally: ## Start web server
	${POETRY} ${PYTHON} src.api.server

##@ Production
.PHONY: setup
.ONESHELL:
setup: ## Set up all dependencies inside docker containers
	docker-compose -f .docker/docker-compose.yaml --env-file .env up -d

.PHONY: clean
.ONESHELL:
clean: setup ## Stop and delete created containers
	docker-compose -f .docker/docker-compose.yaml down