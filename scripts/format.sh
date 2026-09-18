#!/usr/bin/env bash
set -euo pipefail

echo "Formatting Kernel Lab code..."
python -m ruff format src/ tests/
python -m ruff check --fix src/ tests/
