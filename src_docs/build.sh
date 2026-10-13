#!/usr/bin/env bash
# this_file: src_docs/build.sh
# Build the documentation site from src_docs/md/ into docs/ with ProperDocs + MaterialX.
# Usage: src_docs/build.sh          # strict build into ../docs
#        src_docs/build.sh serve    # live preview on http://127.0.0.1:8000
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
properdocs() {
  uvx --python 3.12 --from properdocs==1.6.7 \
    --with mkdocs-materialx==10.1.8 \
    --with pymdown-extensions==11.0.1 \
    properdocs "$@"
}
if [[ "${1:-build}" == serve ]]; then
  shift
  properdocs serve -f mkdocs.yml "$@"
else
  [[ $# -gt 0 && "$1" == build ]] && shift
  properdocs build --strict -f mkdocs.yml "$@"
  touch ../docs/.nojekyll
fi
