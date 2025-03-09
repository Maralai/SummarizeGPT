#!/bin/bash
set -e

# This script runs linting checks on the Python code
# It can be customized for specific projects by setting environment variables:
# - SOURCE_DIRS: Space-separated list of source directories to lint (default: derived from pyproject.toml or setup.py)
# - TEST_DIRS: Space-separated list of test directories to lint (default: "tests")
# - CONFIG_DIR: Directory containing config files (default: .devcontainer/config)
# - SKIP_ISORT: Set to any value to skip isort
# - SKIP_BLACK: Set to any value to skip black
# - SKIP_FLAKE8: Set to any value to skip flake8
# - SKIP_MYPY: Set to any value to skip mypy

# Determine source directories if not explicitly set
if [ -z "$SOURCE_DIRS" ]; then
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

    # If we found a package name and the directory exists, use it
    if [ ! -z "$PACKAGE_NAME" ] && [ -d "$PACKAGE_NAME" ]; then
        SOURCE_DIRS="$PACKAGE_NAME"
    else
        # Default to all directories that look like Python packages
        SOURCE_DIRS=$(find . -maxdepth 2 -type d -not -path "*/\.*" -not -path "./tests*" -not -path "./venv*" -not -path "./env*" -not -path "./build*" -not -path "./dist*" -exec test -e "{}/__init__.py" \; -print)
    fi
fi

# Set default test directory if not explicitly set
TEST_DIRS=${TEST_DIRS:-"tests"}

# Set default config directory
CONFIG_DIR=${CONFIG_DIR:-".devcontainer/config"}

# Check if directories exist
for dir in $SOURCE_DIRS $TEST_DIRS; do
    if [ ! -d "$dir" ]; then
        echo "Warning: Directory $dir does not exist, skipping."
    fi
done

# Run isort if enabled
if [ -z "$SKIP_ISORT" ]; then
    echo "Running isort..."
    if [ -f "$CONFIG_DIR/pyproject.toml" ]; then
        isort --settings-path="$CONFIG_DIR/pyproject.toml" --check-only $SOURCE_DIRS $TEST_DIRS
    else
        isort --profile black --check-only $SOURCE_DIRS $TEST_DIRS
    fi
fi

# Run black if enabled
if [ -z "$SKIP_BLACK" ]; then
    echo "Running black..."
    if [ -f "$CONFIG_DIR/pyproject.toml" ]; then
        black --config="$CONFIG_DIR/pyproject.toml" --check $SOURCE_DIRS $TEST_DIRS
    else
        black --check $SOURCE_DIRS $TEST_DIRS
    fi
fi

# Run flake8 if enabled
if [ -z "$SKIP_FLAKE8" ]; then
    echo "Running flake8..."
    if [ -f "$CONFIG_DIR/.flake8" ]; then
        flake8 --config="$CONFIG_DIR/.flake8" $SOURCE_DIRS $TEST_DIRS
    else
        flake8 $SOURCE_DIRS $TEST_DIRS
    fi
fi

# Run mypy if enabled
if [ -z "$SKIP_MYPY" ]; then
    echo "Running mypy..."
    if [ -f "$CONFIG_DIR/mypy.ini" ]; then
        mypy --config-file="$CONFIG_DIR/mypy.ini" $SOURCE_DIRS
    else
        mypy $SOURCE_DIRS
    fi
fi

echo "All linting checks passed!"