# Makefile for Agent Demo

.PHONY: help install test clean run run-repl examples

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	python -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	python -m pytest tests/ --cov=src --cov-report=html

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .coverage htmlcov/

run: ## Run the agent with a prompt
	python src/main.py "$(PROMPT)"

run-repl: ## Run the agent in REPL mode
	python src/main.py --repl

run-verbose: ## Run the agent with verbose output
	python src/main.py --verbose "$(PROMPT)"

examples: ## Run example scripts
	python examples/basic_usage.py
	python examples/advanced_usage.py

setup: ## Initial setup
	cp .env.example .env
	@echo "Please edit .env file with your API key"

check: ## Check code quality
	python -m flake8 src/
	python -m mypy src/

format: ## Format code
	python -m black src/ tests/
	python -m isort src/ tests/

lint: ## Lint code
	python -m flake8 src/ tests/
	python -m black --check src/ tests/
	python -m isort --check-only src/ tests/