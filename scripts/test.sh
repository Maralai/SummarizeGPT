#!/bin/bash
set -e

echo "Running pytest..."
pytest --cov=summarizeGPT --cov-report=term-missing --cov-report=xml -v