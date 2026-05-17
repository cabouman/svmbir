Considerations for package maintenance:
1. Package metadata (requires-python, dependencies in pyproject.toml)
This declares the minimum you need, not the maximum. The strong community consensus is: never put upper bounds on requires-python or on dependencies in published package metadata. Upper bounds are actively harmful — they prevent users from installing your package alongside other packages that have already moved forward. If numpy>=2.0 breaks something, the right fix is to fix the code, not to block numpy>=2.0. The only exception is when you have a known, tested incompatibility with a specific version.

2. The CI test matrix
This is where you define what you actually support and verify. For 3.10–3.14, you'd have five jobs in GitHub Actions. When 3.15 comes out, you add it to the matrix and see if anything breaks. This is the right place to discover problems early, before users file bugs.

3. The dev environment (install_conda_environment.sh)
This should pin to a specific version (currently 3.10) for a reproducible daily-driver environment. The version you pick here doesn't limit what users can run — it's just what developers work in. Updating this once a year when a new Python ships is reasonable.

4. The CI workflow (.github/workflows/ci.yml)
This defines the test matrix — OS runners and Python versions — that GitHub Actions runs on every push and pull request. It must be kept in sync with `requires-python` in `pyproject.toml`.

Updating Python versions (do this ~once a year):
- **Add a new version**: Each October, Python ships a new release. Add it to the `python-version` list in `ci.yml` and also update `requires-python` in `pyproject.toml` if you are dropping the oldest supported version.
- **Drop an EOL version**: Python versions reach end-of-life roughly 3 years after release (schedule at python.org/downloads). Remove the version from the `python-version` list and raise `requires-python` in `pyproject.toml` to match.

Updating OS runners (do this when GitHub retires a runner):
- The current matrix is `[ubuntu-latest, macos-13, macos-14]`. `macos-13` is Intel (x86_64); `macos-14` is Apple Silicon (arm64). GitHub publishes deprecation notices before retiring runners — when `macos-13` is retired, remove it from the list.
- `ubuntu-latest` and `macos-latest` track GitHub's current default. Pinning to a numbered runner (e.g., `macos-14`) is more explicit and avoids surprise breakage when GitHub moves the `latest` pointer.

5. The release workflow (.github/workflows/release.yml)
This builds binary wheels for all supported platforms and Python versions, then attaches them as downloadable files to a GitHub Release. It is triggered automatically by pushing a version tag.

How to cut a release:
1. Update the version in `pyproject.toml` (the single source of truth — `__init__.py` reads it at runtime via `importlib.metadata`).
2. Commit and push: `git commit -m "Release v0.X.Y" && git push`
3. Tag and push the tag: `git tag v0.X.Y && git push --tags`
4. GitHub Actions picks up the tag, builds wheels on Ubuntu x86_64, macOS Intel (macos-13), and macOS arm64 (macos-14) for Python 3.10–3.12, and creates a GitHub Release with all wheels and the source distribution attached.
5. Verify the release on the repo's Releases page. Users can install directly with `pip install` using the wheel URL, or download manually.

Updating the release workflow over time:
- **Python versions**: keep the `build` setting in `[tool.cibuildwheel]` in `pyproject.toml` in sync with the CI matrix in `ci.yml` and `requires-python`. All three should agree.
- **OS runners**: the release workflow uses the same `[macos-13, macos-14]` matrix as `ci.yml`. Apply the same runner retirement process described above.
- **cibuildwheel version**: `pypa/cibuildwheel@v2.22.0` in `release.yml` is pinned for reproducibility. When a new Python version requires a newer cibuildwheel release, bump the pin.

Adding PyPI distribution later:
When ready to publish to PyPI, add a final job to `release.yml` after `create-release`:
1. Set up PyPI Trusted Publishing in your PyPI project settings (links the GitHub repo without needing a stored API token).
2. Add a `publish-to-pypi` job that downloads the `dist/` artifacts and runs `pypa/gh-action-pypi-publish`.

Keeping current over time — the practical options:

1. Dependabot (built into GitHub): opens automated PRs when dependencies release new versions. Very low friction — it just creates a PR, and your CI tells you if it breaks anything. This is the right tool for routine package bumps.

2. Manual annual review: less automated but sufficient for a project that doesn't change often. When a new Python or NumPy ships, run the test suite against it and fix what breaks.

3. pip-compile / lock files: great for applications that need exact reproducibility, but not the right tool for a library — it over-constrains what users can install alongside you.

For this project specifically, Cython + C extensions have two real compatibility risks:

1. New Python versions: Cython generates standard CPython API code, so new Pythons almost always Just Work once Cython itself is updated. The main friction is that Cython needs to release a version supporting the new Python's ABI before you can build wheels for it.

2. NumPy major versions: NumPy 2.0 changed the C API in breaking ways. We already added NPY_NO_DEPRECATED_API which is the right first step, but a runtime test against NumPy 2.x is worth adding to the CI matrix.