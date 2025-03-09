#!/bin/bash
set -e

echo "Running isort..."
isort --profile black --check-only summarizeGPT tests

echo "Running black..."
black --check summarizeGPT tests

echo "Running flake8..."
flake8 summarizeGPT tests

echo "Running mypy..."
mypy summarizeGPT