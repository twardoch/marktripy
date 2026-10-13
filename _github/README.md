# GitHub Actions Workflows

This directory contains the planned GitHub Actions workflows for the marktripy project. To activate these workflows, copy this directory to `.github` in your repository root.

## Workflows

### `docs.yml` (removed)
Documentation is now built by the active workflow `.github/workflows/docs.yml`,
which runs `src_docs/build.sh` and commits the rebuilt `docs/` folder.
The site is served at https://vexy.dev/vexy-marktripy/.

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
- Check the ProperDocs configuration in `src_docs/mkdocs.yml`
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

## Building the documentation locally

```bash
# Strict build of src_docs/md/ into docs/
src_docs/build.sh

# Live preview on http://127.0.0.1:8000
src_docs/build.sh serve
```
