Considerations for package maintenance:
---------------------------------------

1. Package metadata (requires-python, dependencies in pyproject.toml)
This declares the minimum you need, not the maximum. The strong community consensus is: never put upper bounds on requires-python or on dependencies in published package metadata. Upper bounds are actively harmful — they prevent users from installing your package alongside other packages that have already moved forward. If numpy>=2.0 breaks something, the right fix is to fix the code, not to block numpy>=2.0. The only exception is when you have a known, tested incompatibility with a specific version.

2. The CI test matrix
CI (Continuous Integration) is automated testing that runs in the cloud every time code is pushed to the repository or a pull request is opened. For svmbir, this means GitHub automatically installs the package and runs the test suite on Linux across all supported Python versions. The goal is to catch breakage early — before a bug reaches users — and to confirm that changes work correctly across the Python versions the package claims to support. Check https://github.com/cabouman/svmbir/actions for status.

The CI matrix is the list of Python versions CI tests against. The current matrix is under jobs->matrix->python-version in `ci.yml`. When a new Python version comes out in October, add it to the list and see if anything breaks. This is the right place to discover problems early, before users file bugs.

3. The dev environment (install_conda_environment.sh)
This should pin to a specific recent version for a reproducible daily-driver environment. The version you pick here doesn't limit what users can run — it's just what developers work in. Updating this once a year when a new Python ships is reasonable.

4. The CI workflow (.github/workflows/ci.yml)
This is the configuration file that tells GitHub how to run CI. It specifies which Python versions to test, which operating system to use (Linux only — see section 5 for macOS), and what commands to run (install the package, run pytest). It fires automatically on every push to `master` or `prerelease`, and on every pull request targeting either branch — no manual action needed.

Updating Python versions (do this ~once a year):
- **Add a new version**: Each October, Python ships a new release. Add it to the `python-version` list in `ci.yml`, and add the matching `cp3XX-*` entry to the `build` setting in `[tool.cibuildwheel]` in `pyproject.toml` so release wheels are built for it too. Note that Cython may lag a few months behind a new Python release, so if CI fails on the new version due to a Cython build error, simply remove it from both lists and try again after the next Cython release.
- **Drop an EOL version**: Python versions reach end-of-life roughly 3 years after release (schedule at python.org/downloads). Remove it from the `python-version` list in `ci.yml`, the `build` setting in `pyproject.toml`, and raise `requires-python` in `pyproject.toml` to match.

Updating OS runners:
- CI runs Linux only (`ubuntu-latest`). macOS is no longer in the CI matrix — macOS compatibility is verified when building and test-installing the release wheels locally (see section 5 below).
- If a future Linux runner name change is needed, `ubuntu-latest` tracks GitHub's current default and rarely requires manual updates.

5. The release workflow (.github/workflows/release.yml) and local macOS build
Linux wheels and the source distribution are built automatically by GitHub Actions. macOS arm64 wheels are built locally using `dev_scripts/build_mac_wheels.sh` and uploaded to the same draft release. Intel Mac (x86_64) is no longer supported.

New releases:
-------------

Prerequisites:

- **`cibuildwheel` and `gh`** (the GitHub CLI) are installed automatically by `install_conda_environment.sh`. `gh` is GitHub's official command-line tool — it talks to the GitHub API to create releases and upload wheel files on your behalf, separate from your normal `git` push access. Both scripts detect whether `gh` is authenticated and run `gh auth login` for you if needed (opens a browser to log in to your GitHub account).

- **Official Python.org framework builds** — cibuildwheel builds portable wheels using the official Python installers from python.org, which must be installed system-wide in `/Library/Frameworks/Python.framework/Versions/`. These are entirely separate from conda. Run this one-time setup script (requires sudo):

  ```
  ./install_python_frameworks.sh  
  # Update this script and re-run each time a new python 
  # version is added to ci.yml.
  ```

  The script finds and installs the latest patch release of each supported Python version automatically, skipping any that are already present. Keep this list in sync with the CI matrix in `ci.yml` — the script's `MINOR_VERSIONS` array at the top is the place to update.

Test and release:

Each release is staged on the `prerelease` branch and stays as a non-public draft until you explicitly publish it, so you can verify everything before it goes live. The process has two steps: test first, then release.

Both scripts are run from the `prerelease` branch. The typical sequence after your feature branch PR has been merged into `prerelease`:

   ```
   git checkout prerelease && git pull
   ./test_release.sh      # dry run — verify the pipeline works
   ./cut_release.sh       # real release
   ```

`test_release.sh` warns (but does not exit) if you are not on `prerelease`, so it can also be used from a feature branch to debug a workflow problem.

Note that the scripts need to be run as `./<script>.sh` rather than `source <script>.sh`. 

Step A — Test the release workflow (run before every release):
`./test_release.sh` automates a complete dry run of the release process using a throwaway tag. It:
- Creates and pushes a test tag of the form `v<current_version>-bump-test` (e.g. `v0.4.0-bump-test`), based on the current version in `pyproject.toml`. The wheels built during the test will carry the current version number — this is expected. The real release will update `pyproject.toml` to the new version before building.
- Triggers GitHub Actions to create a draft release and build Linux wheels
- Builds the macOS arm64 wheels locally and uploads them to the same draft release
- Pauses for you to verify that all wheels appear correctly on the GitHub Releases page
- Cleans up the test tag and draft release automatically when you confirm success

Step B — Cut the real release:
Once the test in Step A passes, `./cut_release.sh` does the real release. It:
- Shows the current version and the latest published release, and prompts for the new version
- Validates the new version is greater than the existing one
- Updates `pyproject.toml`, commits, pushes, and creates the version tag
- Triggers GitHub Actions to create a draft release and build Linux wheels
- Builds the macOS arm64 wheels locally and uploads them
- Prints the remaining manual steps: verify the draft release, open the prerelease→master PR, and publish

Manual steps (for reference or recovery if a script fails partway through):
1. On the `prerelease` branch, update the version in `pyproject.toml` to the new version (e.g. `0.4.X`). This is the single source of truth — `__init__.py` reads it at runtime via `importlib.metadata`.
2. Commit and push the version bump: `git commit -m "Release v0.4.X" && git push`
3. Tag the commit and push the tag: `git tag v0.4.X && git push --tags`
   GitHub Actions immediately creates a draft release, then builds Linux wheels and the source distribution and uploads them.
4. Build and upload the macOS arm64 wheels: `cd dev_scripts && ./build_mac_wheels.sh v0.4.X`
5. Go to the repo's Releases page on GitHub and confirm both Linux and macOS wheels are attached.
6. Merge `prerelease` → `master` via a pull request: `gh pr create --base master --title "Release v0.4.X"`
7. After the PR merges, publish the draft release on GitHub.

Updating the release workflow over time:
- **Python versions**: keep the `build` setting in `[tool.cibuildwheel]` in `pyproject.toml` in sync with the CI matrix in `ci.yml` and `requires-python`. All three should agree.
- **cibuildwheel version**: `pypa/cibuildwheel@v2.22.0` in `release.yml` is pinned for reproducibility. When a new Python version requires a newer cibuildwheel release, bump the pin here and also update the version in `install_conda_environment.sh` so local builds stay in sync.

Adding PyPI distribution later:
When ready to publish to PyPI, add a final job to `release.yml` after `create-draft-release`:
1. Set up PyPI Trusted Publishing in your PyPI project settings (links the GitHub repo without needing a stored API token).
2. Add a `publish-to-pypi` job that downloads the `dist/` artifacts and runs `pypa/gh-action-pypi-publish`.


Development workflow: prerelease → master
-----------------------------------------

The standard workflow for this repo is: feature branch → PR to `prerelease` → PR from `prerelease` to `master`. CI runs automatically at both gates.

When working on a feature branch:
1. Push your branch to GitHub: `git push -u origin <branch-name>`
2. Open a pull request to `prerelease`: `gh pr create --base prerelease`
3. GitHub automatically runs CI. Go to the PR page and click the "Checks" tab, or visit https://github.com/cabouman/svmbir/actions, to watch the jobs run (one per Python version on Linux).
4. If a job fails, click into it to read the log, fix the issue, push another commit to the branch, and CI re-runs automatically.
5. Once CI passes, merge the PR into `prerelease`.
6. When ready to release, run `./test_release.sh` then `./cut_release.sh` from dev_scripts/ on the `prerelease` branch.
7. Open a PR from `prerelease` to `master` and merge after CI passes.
8. Publish the draft release on GitHub.


Keeping current over time — the practical options:
--------------------------------------------------

1. Dependabot (built into GitHub): opens automated PRs when dependencies release new versions. Very low friction — it just creates a PR, and your CI tells you if it breaks anything. This is the right tool for routine package bumps.

2. Manual annual review: less automated but sufficient for a project that doesn't change often. When a new Python or NumPy ships, run the test suite against it and fix what breaks.

3. pip-compile / lock files: great for applications that need exact reproducibility, but not the right tool for a library — it over-constrains what users can install alongside you.

For this project specifically, Cython + C extensions have two real compatibility risks:

1. New Python versions: Cython generates standard CPython API code, so new Pythons almost always Just Work once Cython itself is updated. The main friction is that Cython needs to release a version supporting the new Python's ABI before you can build wheels for it.

2. NumPy major versions: NumPy 2.0 changed the C API in breaking ways. We already added NPY_NO_DEPRECATED_API which is the right first step, but a runtime test against NumPy 2.x is worth adding to the CI matrix.
