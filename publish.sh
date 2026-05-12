#!/usr/bin/env bash
# this_file: publish.sh
# Bump the semver git tag, build, and publish to PyPI.
# Requires UV_PUBLISH_TOKEN or `uv publish` interactive auth.
set -euo pipefail
cd "$(dirname "$0")"

gitnextver .
./build.sh
uv publish dist/*
