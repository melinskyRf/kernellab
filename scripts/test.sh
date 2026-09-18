#!/usr/bin/env bash
set -euo pipefail

echo "Running Kernel Lab tests..."
python -m pytest tests/ -v --tb=short "$@"
