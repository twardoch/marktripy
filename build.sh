#!/usr/bin/env bash
# this_file: build.sh
# Build wheel + sdist into dist/ via uv + hatchling.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf dist
uvx hatch clean
uvx hatch build
ls -la dist
