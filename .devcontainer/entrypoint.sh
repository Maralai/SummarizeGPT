#!/bin/bash
set -e

# Change to workspace directory
cd /workspace

echo "🔧 Setting up Python development environment with Claude Code integration..."

# Make scripts executable
find /workspace/.devcontainer/scripts -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Install package in development mode if we're inside the workspace
if [ -f /workspace/setup.py ]; then
    echo "📦 Installing package in development mode..."
    pip install -e .
fi

# Install development dependencies if the file exists
if [ -f /workspace/.devcontainer/config/requirements-dev.txt ]; then
    echo "📚 Installing development dependencies..."
    pip install -r /workspace/.devcontainer/config/requirements-dev.txt
fi

# Run setup-dev.sh if it exists
if [ -f /workspace/.devcontainer/scripts/setup-dev.sh ]; then
    echo "🛠️ Setting up development environment..."
    bash /workspace/.devcontainer/scripts/setup-dev.sh
fi

# Create CLAUDE.md to store project-specific information if it doesn't exist
if [ ! -f /workspace/CLAUDE.md ]; then
    echo "📝 Creating CLAUDE.md file for Claude Code..."
    cat > /workspace/CLAUDE.md << 'EOF'
# Project Information for Claude Code

## Project Overview
SummarizeGPT is a tool that generates a summary of a directory's contents, including a tree view of its subdirectories and files, and the contents of each file. It can exclude files based on .gitignore, filter by extension, and more.

## Development Commands

### Build and Test
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=summarizeGPT

# Build package
python -m build
```

### Lint and Format
```bash
# Run all linters
bash .devcontainer/scripts/lint.sh

# Format code with black
black summarizeGPT tests

# Sort imports with isort
isort summarizeGPT tests
```

### Run the CLI
```bash
# Basic usage
python -m summarizeGPT.summarizeGPT .

# With auto-gitignore discovery
python -m summarizeGPT.summarizeGPT . -ig

# Set verbosity
python -m summarizeGPT.summarizeGPT . -v
```

## Code Structure
- `summarizeGPT/summarizeGPT.py`: Main CLI implementation
- `tests/`: Test suite

## Code Conventions
- 100 character line length
- Black for code formatting
- PEP 8 style guidelines
- Docstrings for all public functions and classes
EOF
fi

# Create Makefile if it doesn't exist
if [ ! -f /workspace/Makefile ]; then
    echo "📋 Creating Makefile..."
    cat > /workspace/Makefile << 'EOF'
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
	pip install -r .devcontainer/config/requirements-dev.txt

lint:
	bash .devcontainer/scripts/lint.sh

test:
	bash .devcontainer/scripts/test.sh

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
EOF
fi

# Setup Python virtual environment if needed for non-container use
if [ ! -d "/workspace/.venv" ] && [ "${SETUP_VENV:-true}" = "true" ]; then
    echo "🐍 Creating Python virtual environment for non-container use..."
    python -m venv /workspace/.venv
    /workspace/.venv/bin/pip install -U pip setuptools wheel
    /workspace/.venv/bin/pip install -e .
    /workspace/.venv/bin/pip install -r /workspace/.devcontainer/config/requirements-dev.txt
fi

# Configure Claude CLI if available
if [ -x "$(command -v claude)" ]; then
    echo "🤖 Setting up Claude CLI..."
    if [ -f "$HOME/.config/claude/config.json" ]; then
        echo "Claude CLI already configured."
    else
        mkdir -p "$HOME/.config/claude"
        echo '{"api_key":"simulated_key"}' > "$HOME/.config/claude/config.json"
        echo "Created placeholder Claude CLI configuration."
    fi
fi

echo "✅ Environment setup complete!"
echo "🚀 Claude Code is ready to use!"

# Execute the command passed to the container
exec "$@"