#!/usr/bin/env bash
# this_file: publish.sh
# Release to PyPI: gitnextver commits pending changes, tags the next vX.Y.Z and
# pushes; then the package is built from that tag and uploaded with uv publish.
# Requires UV_PUBLISH_TOKEN (or another uv publish credential) in the environment.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
uvx gitnextver
tag="$(git describe --tags --exact-match HEAD 2>/dev/null || true)"
if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "HEAD carries no vX.Y.Z tag. gitnextver only tags when there are changes to commit." >&2
  exit 1
fi
./build.sh package
uv publish --check-url https://pypi.org/simple/ dist/*
