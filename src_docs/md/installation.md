# Installation Guide

This guide covers all the ways to install marktripy, from simple pip installations to development setups.

## Quick Installation

### Using pip (Recommended for most users)

```bash
pip install marktripy
```

### Using uv (Fastest and most modern)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install marktripy
uv add marktripy
```

### Using pipx (For CLI usage)

If you primarily want to use marktripy as a command-line tool:

```bash
pipx install marktripy
```

## System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Linux, macOS, Windows
- **Memory**: Minimum 256MB RAM (for processing large documents)

## Virtual Environment Setup

### Using venv

```bash
# Create virtual environment
python -m venv marktripy-env

# Activate (Linux/macOS)
source marktripy-env/bin/activate

# Activate (Windows)
marktripy-env\Scripts\activate

# Install marktripy
pip install marktripy
```

### Using uv (Recommended)

```bash
# Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install marktripy
uv add marktripy
```

## Development Installation

### Clone and Install for Development

```bash
# Clone the repository
git clone https://github.com/twardoch/marktripy
cd marktripy

# Install in development mode with uv
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Development Dependencies

The development installation includes additional tools:

- **Testing**: `pytest`, `pytest-benchmark`, `pytest-cov`, `hypothesis`
- **Code Quality**: `ruff`, `black`, `mypy`
- **Build Tools**: `hatch`, `twine`

### Running Tests

```bash
# Run all tests
pytest

# Run tests without benchmarks (faster)
pytest -k 'not benchmark'

# Run with coverage
pytest --cov=marktripy --cov-report=html

# Run only benchmarks
pytest -k benchmark
```

### Using Hatch (Alternative Development Setup)

```bash
# Install hatch
pip install hatch

# Run tests in isolated environment
hatch test

# Run specific test commands
hatch run test:cov
hatch run test:benchmark
```

## Dependency Management

### Core Dependencies

marktripy requires these packages:

```toml
dependencies = [
    "fire>=0.7.0",           # CLI framework
    "loguru>=0.7.3",         # Logging
    "markdown-it-py[linkify,plugins]>=3.0.0",  # Primary parser
    "mistletoe>=1.4.0",      # Alternative parser
    "rich>=14.1.0",          # Terminal formatting
]
```

### Optional Dependencies

For enhanced functionality, you can install additional packages:

```bash
# For performance (C-based parser)
pip install umarkdown

# For math extensions
pip install markdown-it-py[math]

# For diagram support
pip install markdown-it-py[mermaid]
```

## Installation Verification

### Basic Verification

```bash
# Check installation
python -c "import marktripy; print(marktripy.__version__)"

# Test CLI
marktripy --help
```

### Full Test Suite

```bash
# Run a simple test
python -c "
from marktripy import parse_markdown, render_markdown
ast = parse_markdown('# Hello World')
print('✓ marktripy is working correctly')
"
```

### Performance Test

```bash
# Run benchmark to verify performance
python -c "
import time
from marktripy import parse_markdown

start = time.time()
for i in range(100):
    parse_markdown('# Test ' + str(i))
elapsed = time.time() - start
print(f'✓ Parsed 100 documents in {elapsed:.3f}s')
"
```

## Troubleshooting

### Common Issues

#### Import Error: No module named 'marktripy'

**Problem**: Python can't find the marktripy module.

**Solutions**:
```bash
# Verify installation
pip list | grep marktripy

# Reinstall if missing
pip install --force-reinstall marktripy

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Permission Denied on Installation

**Problem**: Insufficient permissions to install packages.

**Solutions**:
```bash
# Install for current user only
pip install --user marktripy

# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install marktripy
```

#### Version Conflicts

**Problem**: Dependency version conflicts.

**Solutions**:
```bash
# Check for conflicts
pip check

# Create fresh environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install marktripy

# Use uv for better dependency resolution
uv add marktripy
```

#### Slow Installation

**Problem**: Installation takes too long.

**Solutions**:
```bash
# Use uv for faster installation
curl -LsSf https://astral.sh/uv/install.sh | sh
uv add marktripy

# Use pip with cache
pip install --cache-dir ~/.pip/cache marktripy

# Install from wheel
pip install --only-binary=all marktripy
```

### Platform-Specific Issues

#### Windows

```bash
# Use long path support
pip install --user --upgrade marktripy

# If using Windows Subsystem for Linux (WSL)
sudo apt update
sudo apt install python3-pip
pip install marktripy
```

#### macOS

```bash
# Install Python if needed
brew install python

# Install marktripy
pip3 install marktripy

# For M1/M2 Macs, ensure compatible dependencies
pip install --upgrade pip setuptools wheel
pip install marktripy
```

#### Linux

```bash
# Install Python development headers if needed
sudo apt-get install python3-dev  # Ubuntu/Debian
sudo yum install python3-devel    # CentOS/RHEL
sudo dnf install python3-devel    # Fedora

# Install marktripy
pip install marktripy
```

## Docker Installation

### Using Official Python Image

```dockerfile
FROM python:3.12-slim

# Install marktripy
RUN pip install marktripy

# Copy your scripts
COPY . /app
WORKDIR /app

# Run your application
CMD ["python", "your_script.py"]
```

### Build and Run

```bash
# Build image
docker build -t marktripy-app .

# Run container
docker run -v $(pwd):/app marktripy-app
```

## Next Steps

Once you have marktripy installed:

1. **Try the [Quick Start](quickstart.md)** examples
2. **Read about [Core Concepts](core-concepts.md)** to understand the architecture
3. **Explore the [CLI Usage](cli.md)** for command-line tools
4. **Check out [AST Manipulation](ast-manipulation.md)** for programmatic document editing

## Getting Help

If you encounter installation issues:

1. **Check the [GitHub Issues](https://github.com/twardoch/marktripy/issues)** for known problems
2. **Create a new issue** with your error message and system information
3. **Join the discussions** for community support

Include this information when reporting issues:

```bash
# System information
python --version
pip --version
pip list | grep marktripy

# Error message
# (copy the full error output)
```