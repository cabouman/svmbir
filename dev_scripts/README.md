Considerations for package maintenance:
---------------------------------------

1. Package metadata (requires-python, dependencies in pyproject.toml)
This declares the minimum you need, not the maximum. The strong community consensus is: never put upper bounds on requires-python or on dependencies in published package metadata. Upper bounds are actively harmful — they prevent users from installing your package alongside other packages that have already moved forward. If numpy>=2.0 breaks something, the right fix is to fix the code, not to block numpy>=2.0. The only exception is when you have a known, tested incompatibility with a specific version.

2. The CI test matrix
CI (Continuous Integration) is automated testing that runs in the cloud every time code is pushed to the repository or a pull request is opened. For svmbir, this means GitHub automatically installs the package and runs the test suite on Linux across all supported Python versions. The goal is to catch breakage early — before a bug reaches users — and to confirm that changes work correctly across the Python versions the package claims to support.

The CI matrix is the list of Python versions CI tests against. The current matrix is under jobs->matrix->python-version in `ci.yml`. When a new python version comes out in October, add it to the list and see if anything breaks. This is the right place to discover problems early, before users file bugs.

3. The dev environment (install_conda_environment.sh)
This should pin to a specific recent version for a reproducible daily-driver environment. The version you pick here doesn't limit what users can run — it's just what developers work in. Updating this once a year when a new Python ships is reasonable.

4. The CI workflow (.github/workflows/ci.yml)
This is the configuration file that tells GitHub how to run CI. It specifies which Python versions to test, which operating system to use (Linux only — see section 5 for macOS), and what commands to run (install the package, run pytest). It fires automatically on every push to `master` or `prerelease`, and on every pull request targeting either branch — no manual action needed.

Updating Python versions (do this ~once a year):
- **Add a new version**: Each October, Python ships a new release. Add it to the `python-version` list in `ci.yml`, and add the matching `cp3XX-*` entry to the `build` setting in `[tool.cibuildwheel]` in `pyproject.toml` so release wheels are built for it too.
- **Drop an EOL version**: Python versions reach end-of-life roughly 3 years after release (schedule at python.org/downloads). Remove it from the `python-version` list in `ci.yml`, the `build` setting in `pyproject.toml`, and raise `requires-python` in `pyproject.toml` to match.

Updating OS runners:
- CI runs Linux only (`ubuntu-latest`). macOS is no longer in the CI matrix — macOS compatibility is verified when building and test-installing the release wheels locally (see section 5 below).
- If a future Linux runner name change is needed, `ubuntu-latest` tracks GitHub's current default and rarely requires manual updates.

5. The release workflow (.github/workflows/release.yml) and local macOS build
Linux wheels and the source distribution are built automatically by GitHub Actions. macOS arm64 wheels are built locally using `dev_scripts/build_mac_wheels.sh` and uploaded to the same draft release. Intel Mac (x86_64) is no longer supported.

How to cut a release:
---------------------

All steps up to and including tagging are done on the `prerelease` branch. The release stays as a non-public draft until you explicitly publish it, so you can verify everything before it goes live.

**The normal release is done with a single command in dev_scripts/ (and using this form, *not* `source cut_release.sh`):**

   `./cut_release.sh`

The script runs all preflight checks, prompts for the new version (showing the current pyproject.toml version and the latest published release for reference), asks for confirmation, then automates steps 1–5 below. If the script fails partway through, the manual steps below can be used to complete the release.

Prerequisites: `cibuildwheel` and `gh` (the GitHub CLI) are both installed automatically by `install_conda_environment.sh`. `gh` is GitHub's official command-line tool — it talks to the GitHub API to create releases and upload wheel files on your behalf, separate from your normal `git` push access. One extra one-time step after running the environment script: `gh auth login` (opens a browser to authenticate with your GitHub account).

Manual steps (for reference or recovery):
1. On the `prerelease` branch, update the version in `pyproject.toml` to the new version (e.g. `0.4.X`). This is the single source of truth — `__init__.py` reads it at runtime via `importlib.metadata`.
2. Commit and push the version bump: `git commit -m "Release v0.4.X" && git push`
3. Tag the commit and push the tag: `git tag v0.4.X && git push --tags`
   GitHub Actions immediately creates a draft release, then builds Linux wheels and the source distribution and uploads them.
4. Build and upload the macOS arm64 wheels (requires `gh auth login` done once): `cd dev_scripts && ./build_mac_wheels.sh v0.4.X`
5. Go to the repo's Releases page on GitHub and confirm both Linux and macOS wheels are attached.
6. Merge `prerelease` → `master` via a pull request: `gh pr create --base master --title "Release v0.4.X"`
7. After the PR merges, publish the draft release on GitHub.

Updating the release workflow over time:
- **Python versions**: keep the `build` setting in `[tool.cibuildwheel]` in `pyproject.toml` in sync with the CI matrix in `ci.yml` and `requires-python`. All three should agree.
- **cibuildwheel version**: `pypa/cibuildwheel@v2.22.0` in `release.yml` is pinned for reproducibility. When a new Python version requires a newer cibuildwheel release, bump the pin here and also update the version in `install_conda_environment.sh` so local builds stay in sync.

Testing the workflows — prerelease → master flow:
-------------------------------------------------

The standard workflow for this repo is: feature branch → PR to `prerelease` (for integration testing) → PR from `prerelease` to `master` (for release). The CI workflow is configured to fire on PRs targeting either `prerelease` or `master`, so it runs at both gates automatically.

Step 1 — Test the CI workflow via a PR to prerelease:
GitHub Actions fires the `pull_request` trigger using the workflow file from the PR's source branch, not the target branch. This means the workflow is tested as it exists in your branch, before anything is merged.

1. Push your branch to GitHub if you haven't already:
   `git push -u origin <branch-name>`
2. Open a pull request from your branch to `prerelease` (not master) on the GitHub website, or with:
   `gh pr create --base prerelease`
3. GitHub automatically starts the CI workflow. Go to the PR page and click the "Checks" tab, or go to the repo's "Actions" tab, to watch the 3 jobs (3 Python versions × 1 OS runner: Linux) run.
4. If any job fails, click into it to read the log, fix the issue, push another commit to the branch, and the workflow re-runs automatically.
5. Once CI passes, merge the PR into `prerelease`.

Step 2 — Bump the version, then test the release workflow via a test tag:
The release workflow triggers on a version tag, which is repo-wide. GitHub uses the `release.yml` from the commit the tag points to — so tagging a commit on `prerelease` exercises the workflow as it exists there, before the final merge to `master`. This is also the right point to update the version number, since the tag and the version in the package should always match.

1. Update the version in `pyproject.toml` to the intended release version (e.g. `0.4.X`). This is the single source of truth — `__init__.py` reads it at runtime via `importlib.metadata`.
2. Commit and push the version bump:
   `git commit -m "Release v0.4.X" && git push`
3. Push a test tag pointing to that commit:
   `git tag v0.4.X-test && git push --tags`
4. Go to the repo's "Actions" tab on GitHub and watch the release workflow run. It creates a draft release, then builds Linux wheels and the source distribution and uploads them.
5. While that runs (or after), test the local macOS build:
   `cd dev_scripts && ./build_mac_wheels.sh v0.4.X-test`
6. Go to the repo's "Releases" page to confirm the draft release was created and all wheel files (`.whl`) and the source distribution (`.tar.gz`) are attached. You can test-install a wheel directly:
   `pip install <URL copied from the release page>`
7. Clean up when done — delete the test tag and release (do NOT publish the draft):
   - Delete the release: go to the Releases page, click the test release, click "Delete" (trash icon).
   - Delete the remote tag: `git push --delete origin v0.4.X-test`
   - Delete the local tag: `git tag -d v0.4.X-test`

Step 3 — PR from prerelease to master:
Once everything looks good on `prerelease`, open a PR from `prerelease` to `master`. CI runs again on this PR. When it passes, merge — from this point on, every push to `master` or `prerelease` runs CI automatically, and every version tag triggers a real release build.

Adding PyPI distribution later:
When ready to publish to PyPI, add a final job to `release.yml` after `create-release`:
1. Set up PyPI Trusted Publishing in your PyPI project settings (links the GitHub repo without needing a stored API token).
2. Add a `publish-to-pypi` job that downloads the `dist/` artifacts and runs `pypa/gh-action-pypi-publish`.

Keeping current over time — the practical options:
--------------------------------------------------

1. Dependabot (built into GitHub): opens automated PRs when dependencies release new versions. Very low friction — it just creates a PR, and your CI tells you if it breaks anything. This is the right tool for routine package bumps.

2. Manual annual review: less automated but sufficient for a project that doesn't change often. When a new Python or NumPy ships, run the test suite against it and fix what breaks.

3. pip-compile / lock files: great for applications that need exact reproducibility, but not the right tool for a library — it over-constrains what users can install alongside you.

For this project specifically, Cython + C extensions have two real compatibility risks:

1. New Python versions: Cython generates standard CPython API code, so new Pythons almost always Just Work once Cython itself is updated. The main friction is that Cython needs to release a version supporting the new Python's ABI before you can build wheels for it.

2. NumPy major versions: NumPy 2.0 changed the C API in breaking ways. We already added NPY_NO_DEPRECATED_API which is the right first step, but a runtime test against NumPy 2.x is worth adding to the CI matrix.