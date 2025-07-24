## You can follow the steps below in order to get yourself a local ODC.
## Start by running `setup` then you should have a system that is fully configured

IMAGE_NAME := openeo_odc_driver:test

.PHONY: help setup up down clean

BBOX := 11,45,12,46

help: ## Print this help
	@grep -E '^##.*$$' $(MAKEFILE_LIST) | cut -c'4-'
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: build up test ## Run a full local/development setup

test: ## Run the process graph test inside the container
	docker compose exec openeo_odc_driver bash -c "cd /openeo_odc_driver && conda run -n openeo_odc_driver pytest tests/pytests.py"
	docker compose exec openeo_odc_driver bash -c "cd /openeo_odc_driver && conda run -n openeo_odc_driver python tests/zarr_test.py ./tests/process_graphs/zarr_process_graph.json"

update: build up ## Update and bring up the environment

up: ## 1. Bring up your Docker environment
	docker compose up -d --remove-orphans openeo_odc_driver

down: ## Bring down the system
	docker compose down

build: ## Rebuild the base image, deleting old one if exists
	@if docker image inspect $(IMAGE_NAME) > /dev/null 2>&1; then \
		echo "Removing existing image: $(IMAGE_NAME)"; \
		docker rmi -f $(IMAGE_NAME); \
	fi
	docker compose build

shell: ## Start an interactive shell
	docker compose exec openeo_odc_driver bash

clean: ## Delete everything
	docker compose down --rmi all -v

logs: ## Show the logs from the stack
	docker compose logs --follow
