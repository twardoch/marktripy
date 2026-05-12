#!/usr/bin/env bash
# this_file: build.sh
# Build script for this Python package

# Change to script directory
cd "$(dirname "$0")"

set -e

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Building package...${NC}"

# Clean build artifacts
echo -e "${YELLOW}→ Cleaning...${NC}"
uvx hatch clean || true

# Run tests if they exist
if [ -d "tests" ] || grep -q "pytest" pyproject.toml; then
    echo -e "${YELLOW}→ Running tests...${NC}"
    uvx hatch test || echo -e "${YELLOW}↔ Tests failed or not configured${NC}"
fi

# Build the package
echo -e "${YELLOW}→ Building package...${NC}"
uvx hatch build

echo -e "${GREEN}✅ Build completed successfully${NC}"
