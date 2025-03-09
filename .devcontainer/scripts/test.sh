#!/bin/bash
set -e

# This script runs tests with pytest
# It can be customized for specific projects by setting environment variables:
# - PACKAGE_NAME: Name of the package to test (default: derived from pyproject.toml or setup.py)
# - TEST_DIRS: Space-separated list of test directories (default: "tests")
# - CONFIG_DIR: Directory containing config files (default: .devcontainer/config)
# - PYTEST_ARGS: Additional arguments to pass to pytest (default: "")
# - COVERAGE_REPORT: Type of coverage report (default: "term-missing")
# - NO_COVERAGE: Set to any value to disable coverage reporting

# Determine package name if not explicitly set
if [ -z "$PACKAGE_NAME" ]; then
    # Try to extract from pyproject.toml or setup.py
    if [ -f "pyproject.toml" ]; then
        # Try to extract from pyproject.toml
        PACKAGE_NAME=$(grep -o 'name\s*=\s*"[^"]*"' pyproject.toml | head -1 | cut -d'"' -f2)
        if [ -z "$PACKAGE_NAME" ]; then
            PACKAGE_NAME=$(grep -o "name\s*=\s*'[^']*'" pyproject.toml | head -1 | cut -d"'" -f2)
        fi
    elif [ -f "setup.py" ]; then
        # Try to extract from setup.py
        PACKAGE_NAME=$(grep -o 'name\s*=\s*"[^"]*"' setup.py | head -1 | cut -d'"' -f2)
        if [ -z "$PACKAGE_NAME" ]; then
            PACKAGE_NAME=$(grep -o "name\s*=\s*'[^']*'" setup.py | head -1 | cut -d"'" -f2)
        fi
    fi

    # If the package name contains hyphens, convert to underscore for Python imports
    if [ ! -z "$PACKAGE_NAME" ]; then
        PACKAGE_DIR=$(echo "$PACKAGE_NAME" | tr '-' '_')
        # Check if directory exists, otherwise use the original name
        if [ ! -d "$PACKAGE_DIR" ]; then
            PACKAGE_DIR="$PACKAGE_NAME"
        fi
    else
        # Default to first directory that looks like a Python package
        PACKAGE_DIR=$(find . -maxdepth 2 -type d -not -path "*/\.*" -not -path "./tests*" -not -path "./venv*" -not -path "./env*" -not -path "./build*" -not -path "./dist*" -exec test -e "{}/__init__.py" \; -print | head -1)
        PACKAGE_DIR=${PACKAGE_DIR#./}  # Remove leading ./
    fi
else
    # If package name is explicitly set, use it for package directory
    PACKAGE_DIR="$PACKAGE_NAME"
    # Check if the directory exists with underscores instead of hyphens
    UNDERSCORE_DIR=$(echo "$PACKAGE_NAME" | tr '-' '_')
    if [ ! -d "$PACKAGE_DIR" ] && [ -d "$UNDERSCORE_DIR" ]; then
        PACKAGE_DIR="$UNDERSCORE_DIR"
    fi
fi

# Set default test directory if not explicitly set
TEST_DIRS=${TEST_DIRS:-"tests"}

# Set default config directory
CONFIG_DIR=${CONFIG_DIR:-".devcontainer/config"}

# Set default coverage report type
COVERAGE_REPORT=${COVERAGE_REPORT:-"term-missing"}

# Build pytest command
PYTEST_CMD="pytest"

# Add verbosity
PYTEST_CMD="$PYTEST_CMD -v"

# Add configuration file if it exists
if [ -f "$CONFIG_DIR/pyproject.toml" ]; then
    PYTEST_CMD="$PYTEST_CMD -c $CONFIG_DIR/pyproject.toml"
fi

# Add coverage if enabled
if [ -z "$NO_COVERAGE" ] && [ ! -z "$PACKAGE_DIR" ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=$PACKAGE_DIR --cov-report=$COVERAGE_REPORT"
    
    # Add XML coverage report for CI
    if [ ! -z "$CI" ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=xml"
    fi
fi

# Add test directories
for dir in $TEST_DIRS; do
    if [ -d "$dir" ]; then
        PYTEST_CMD="$PYTEST_CMD $dir"
    else
        echo "Warning: Test directory $dir does not exist, skipping."
    fi
done

# Add any additional arguments
if [ ! -z "$PYTEST_ARGS" ]; then
    PYTEST_CMD="$PYTEST_CMD $PYTEST_ARGS"
fi

# Run the tests
echo "Running tests with command: $PYTEST_CMD"
$PYTEST_CMD

echo "All tests passed!"