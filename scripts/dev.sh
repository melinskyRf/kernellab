#!/usr/bin/env bash
set -euo pipefail

echo "Starting Kernel Lab development server..."
uvicorn kernellab.api.app:app --reload --host 0.0.0.0 --port 8000
