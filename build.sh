#!/usr/bin/env bash
# this_file: build.sh
# Build the documentation (docs/) and the Python package (dist/).
# Usage: ./build.sh [all|docs|package]   (default: all)
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
target="${1:-all}"
case "$target" in
  all|docs|package) ;;
  *) echo "usage: $0 [all|docs|package]" >&2; exit 2 ;;
esac
if [[ "$target" == all || "$target" == docs ]]; then
  src_docs/build.sh
fi
if [[ "$target" == all || "$target" == package ]]; then
  rm -rf dist
  uv build
  uvx twine check dist/*
fi
