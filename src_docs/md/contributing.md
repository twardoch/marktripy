# Contributing

Prerequisites: Git, `uv`, and a clone of `https://github.com/vexyart/vexy-marktripy`. The default branch is `master`.

## Set up the environment

```bash
uv sync --dev
```

This creates `.venv/`, installs the package in editable mode and adds the `dev` dependency group (`pytest`, `pytest-benchmark`, `pytest-cov`, `hypothesis`, `mypy`, `ruff`, `black`, `twine`, `hatch`).

## Run the tests

```bash
uv run pytest -q
```

The suite lives in `tests/`:

| File | Covers |
|---|---|
| `test_basic.py` | Parser registration, HTML rendering, AST methods |
| `test_roundtrip.py` | Markdown → AST → Markdown |
| `test_transformers.py` | Heading, ID and TOC transformers |
| `test_gfm_extensions.py` | Strikethrough, task lists, the GFM bundle |
| `test_kbd_extension.py` | `++key++` parsing and rendering |
| `test_hypothesis.py` | Property-based tests with `hypothesis` |
| `test_benchmark.py` | Timing benchmarks with `pytest-benchmark` |

Skip the benchmarks for a faster run. `-k` matches test and file names, so this deselects everything in `test_benchmark.py`:

```bash
uv run pytest -q -k "not benchmark"
```

`hatch` environments are also configured. `uvx hatch test` runs the suite in hatch's test environment, and `hatch run test:no-benchmark` runs `pytest -k 'not benchmark'`.

## Lint and type-check

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src/marktripy
```

`ruff` and `black` use a line length of 100. `mypy` is configured with `strict = true`.

## Build the package

```bash
./build.sh package
```

This removes `dist/`, runs `uv build` and checks the result with `twine check`. The version comes from the latest Git tag through `hatch-vcs`; the build writes it to `src/marktripy/_version.py`, which is ignored by Git. Between tags the version has a development suffix such as `1.0.5.dev1+g<commit>`.

## Build the documentation

The documentation sources are the Markdown files in `src_docs/md/`. The configuration is `src_docs/mkdocs.yml`. The site is built with ProperDocs and the MaterialX theme into `docs/`, which GitHub Pages serves at <https://vexy.dev/vexy-marktripy/>.

1. Edit or add pages in `src_docs/md/`. Add new pages to `nav` in `src_docs/mkdocs.yml`.
2. Preview the site while you edit:

    ```bash
    src_docs/build.sh serve
    ```

    The preview runs at `http://127.0.0.1:8000`.

3. Run the strict build. It fails on any warning, such as a broken link or a page missing from `nav`:

    ```bash
    ./build.sh docs
    ```

4. Commit both `src_docs/` and the regenerated `docs/`.

On every push to `master` that touches `src_docs/`, the `Docs` workflow (`.github/workflows/docs.yml`) rebuilds `docs/` and commits the result.

## Release

`./publish.sh` releases to PyPI:

1. `uvx gitnextver` commits pending changes, creates the next `vX.Y.Z` tag and pushes.
2. The script stops if `HEAD` has no `vX.Y.Z` tag.
3. `./build.sh package` builds and checks `dist/`.
4. `uv publish dist/*` uploads. It needs a credential such as `UV_PUBLISH_TOKEN` in the environment.

Pushing the tag also starts the `Release` workflow (`.github/workflows/release.yml`). It builds the package, creates a GitHub release with the files, and uploads to PyPI with `twine upload --skip-existing`, so it does not fail when `publish.sh` already uploaded that version.

## Where to help

The [Known limitations](limitations.md) page lists confirmed defects, each with a reproduction. Fixing one of them, with a test, is the most useful contribution.
