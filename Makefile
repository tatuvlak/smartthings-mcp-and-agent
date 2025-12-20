.PHONY: help install install-dev install-all lint format type-check test test-cov run-agent run-server clean

help:
	@echo "Smart Home MCP Server & Agent - Available Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install package"
	@echo "  make install-dev      Install with dev dependencies"
	@echo "  make install-all      Install with all optional dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             Run ruff linter"
	@echo "  make format           Format code with black"
	@echo "  make type-check       Run mypy type checking"
	@echo "  make lint-all         Run all linting checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run pytest"
	@echo "  make test-cov         Run tests with coverage"
	@echo ""
	@echo "Running:"
	@echo "  make run-agent        Run agent demo"
	@echo "  make run-server       Run MCP server"
	@echo "  make run-chat         Run interactive chat"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache and temp files"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[dev,all]"

lint:
	ruff check src/ tests/

format:
	black src/ tests/

type-check:
	mypy src/

lint-all: lint type-check
	@echo "All checks passed!"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

run-agent:
	python -m src.main agent --log-level INFO

run-server:
	python -m src.main server --log-level INFO

run-chat:
	python -m src.main chat --log-level DEBUG

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	@echo "Cleaned up cache and build artifacts"
