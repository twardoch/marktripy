#!/usr/bin/env bash
# this_file: publish.sh
# Publish script for this Python package
# Workflow: clean → gitnextver → build → publish

# Change to script directory
cd "$(dirname "$0")"

set -e

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

publish_to_pypi() {
    local max_attempts="${PYPI_PUBLISH_MAX_ATTEMPTS:-6}"
    local delay="${PYPI_PUBLISH_INITIAL_DELAY:-300}"
    local max_delay="${PYPI_PUBLISH_MAX_DELAY:-3600}"
    local attempt=1
    local status=0
    local retry_pattern="429|Too Many Requests|too many new projects created|timeout|timed out|temporarily unavailable|502|503|504|connection reset|network"
    local log_file
    local errexit_was_set=0

    case $- in
        *e*) errexit_was_set=1 ;;
    esac

    log_file="$(mktemp "${TMPDIR:-/tmp}/uv-publish.XXXXXX")"

    while [ "$attempt" -le "$max_attempts" ]; do
        : > "$log_file"
        set +e
        uv publish "$@" 2>&1 | tee "$log_file"
        status=${PIPESTATUS[0]}
        if [ "$errexit_was_set" -eq 1 ]; then
            set -e
        else
            set +e
        fi

        if [ "$status" -eq 0 ]; then
            rm -f "$log_file"
            return 0
        fi

        if ! grep -Eiq "$retry_pattern" "$log_file"; then
            echo "PyPI publish failed with a non-retryable error. Not retrying."
            rm -f "$log_file"
            return "$status"
        fi

        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "PyPI publish still failed after $max_attempts attempts."
            echo "If this is PyPI new-project rate limiting, wait for the quota window to reset before rerunning."
            rm -f "$log_file"
            return "$status"
        fi

        local jitter=$((RANDOM % 31))
        local sleep_for=$((delay + jitter))

        if grep -Eiq "too many new projects created" "$log_file"; then
            echo "PyPI is rate-limiting new project creation. This can require a long wait; retrying with backoff."
        fi

        echo "Retrying PyPI publish in ${sleep_for}s (attempt $((attempt + 1))/$max_attempts)..."
        sleep "$sleep_for"

        attempt=$((attempt + 1))
        delay=$((delay * 2))
        if [ "$delay" -gt "$max_delay" ]; then
            delay="$max_delay"
        fi
    done

    rm -f "$log_file"
    return "$status"
}

echo -e "${BLUE}Publishing package...${NC}"
echo -e "${YELLOW}Workflow: clean → gitnextver → build → publish${NC}"

# Step 1: Clean build artifacts
echo -e "${YELLOW}→ Cleaning...${NC}"
uvx hatch clean || true

# Step 2: Run gitnextver to create version tag
echo -e "${YELLOW}→ Running gitnextver...${NC}"
uvx gitnextver || echo -e "${YELLOW}↔ gitnextver failed${NC}"

# Step 3: Build the package
echo -e "${YELLOW}→ Building package...${NC}"
uvx hatch build

# Step 4: Publish to PyPI using uv (NOT uvx hatch publish)
echo -e "${YELLOW}→ Publishing to PyPI...${NC}"
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    publish_to_pypi dist/*
else
    echo -e "${RED}❌ No distribution files found in dist/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package published successfully${NC}"
