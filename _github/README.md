# GitHub Actions Workflows

This directory contains the planned GitHub Actions workflows for the marktripy project. To activate these workflows, copy this directory to `.github` in your repository root.

## Workflows

### `docs.yml`
Builds and deploys MkDocs documentation to GitHub Pages.

**Triggers:**
- Push to `master`/`main` branch with changes to `src_docs/`
- Pull requests modifying documentation

**Features:**
- Builds documentation from `src_docs/` using MkDocs Material theme
- Deploys to GitHub Pages automatically
- Uses caching for faster builds
- Strict mode to catch documentation errors

### `test.yml`
Runs the test suite for the marktripy package.

**Triggers:**
- Push to `master`/`main` branch
- All pull requests

**Features:**
- Tests on Ubuntu, Windows, and macOS
- Uses Python 3.12
- Runs with hatch for dependency management
- Includes linting and type checking

### `dependabot.yml`
Keeps dependencies up to date automatically.

**Features:**
- Weekly updates for Python dependencies
- Weekly updates for GitHub Actions
- Configurable pull request limits

## Setup Instructions

1. **Copy to .github directory:**
   ```bash
   cp -r _github .github
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Set Source to "GitHub Actions"

3. **Configure branch protection (optional):**
   - Require status checks to pass before merging
   - Require up-to-date branches before merging

4. **Set up secrets (if needed):**
   - No additional secrets required for basic setup
   - GitHub automatically provides necessary tokens

## Customization

### Documentation Build
Modify `docs.yml` to:
- Change Python version
- Add additional MkDocs plugins
- Customize build commands
- Change deployment targets

### Testing
Modify `test.yml` to:
- Add more Python versions
- Change operating systems
- Add additional test commands
- Configure code coverage

### Dependency Updates
Modify `dependabot.yml` to:
- Change update frequency
- Modify pull request limits
- Add additional package ecosystems

## Troubleshooting

### Documentation Build Fails
- Check MkDocs configuration in `src_docs/mkdocs.yml`
- Verify all documentation files are valid Markdown
- Ensure all links are working

### Tests Fail
- Check test configuration in `pyproject.toml`
- Verify all dependencies are properly specified
- Check for platform-specific issues

### Pages Deployment Issues
- Ensure GitHub Pages is enabled
- Check that the repository is public (or GitHub Pro/Team for private repos)
- Verify the workflow has necessary permissions

## Manual Deployment

To build and deploy documentation manually:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material mkdocstrings[python]

# Build documentation
cd src_docs
mkdocs build

# Serve locally for testing
mkdocs serve
```

The built documentation will be in the `docs/` directory, ready for deployment to any static hosting service.