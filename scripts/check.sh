#!/usr/bin/env bash
# Run the project's dev checks: lint, then tests with coverage.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== ruff =="
ruff check .

echo
echo "== pytest --cov =="
pytest --cov=text_dungeon --cov-report=term-missing
