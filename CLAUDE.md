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
