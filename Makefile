.PHONY: help install dev lint test clean build publish

help:
	@echo "Available commands:"
	@echo "  make install        Install the package"
	@echo "  make dev            Install development dependencies"
	@echo "  make lint           Run linting checks"
	@echo "  make test           Run tests"
	@echo "  make clean          Clean build artifacts"
	@echo "  make build          Build package"
	@echo "  make publish        Upload package to PyPI"

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

lint:
	./scripts/lint.sh

test:
	./scripts/test.sh

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

build: clean
	python -m build

publish: build
	python -m twine upload dist/*