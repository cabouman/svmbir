# Handover notes — svmbir packaging modernisation
Last updated: 2026-05-19

## Current state

The `prerelease` branch contains a complete, tested release pipeline.
Everything described below is already committed and pushed.  The next step
is to cut the real release and merge `prerelease` → `master`.

### What has been done

**Build system and setup.py**
- `setup.py` detects the platform and selects the right compiler and OpenMP
  library automatically (clang + libomp on macOS arm64, gcc + libgomp on
  Linux).
- Fail-fast checks at the top of `setup.py`: uninitialized git submodule,
  compiler not on PATH, libomp not found on macOS — all exit immediately
  with a clear error message and fix instructions.
- `dev_scripts/install_svmbir.sh` runs `git submodule update --init
  --recursive` before pip install so fresh clones just work.

**GitHub Actions**
- `ci.yml`: runs on every push/PR to `master` or `prerelease`; tests on
  Linux across Python 3.10–3.14; uses conda + llvm-openmp.
- `release.yml`: fires on any version tag push; creates a draft GitHub
  Release immediately, then builds Linux wheels (x86_64 + i686) and the
  sdist and attaches them to the draft.
- `publish.yml`: fires when the draft release is **published** (the manual
  click); downloads all attached assets and uploads them to PyPI via
  Trusted Publishing (OIDC — no stored API token).

**Release scripts** (all in `dev_scripts/`):
- `install_python_frameworks.sh` — installs official Python.org framework
  builds required by cibuildwheel (separate from conda).
- `install_conda_environment.sh` — creates the `svmbir` conda env with
  cibuildwheel and the `gh` CLI pre-installed.
- `test_release.sh` — dry run: pushes a `-bump-test` tag, builds all
  wheels, pauses for verification, cleans up automatically.
- `cut_release.sh` — real release: bumps the version in `pyproject.toml`,
  commits, tags, triggers GitHub Actions, builds macOS wheels locally,
  prints remaining manual steps.
- `build_mac_wheels.sh` — builds macOS arm64 wheels using cibuildwheel and
  uploads them to the draft release.  Called by the two scripts above.
- `test_pypi.sh` — downloads the draft release assets via `gh release
  download`, installs into a clean conda env, runs pytest.  Run this before
  publishing.

**Version management**
- Single source of truth: `version` field in `pyproject.toml`.
- `__init__.py` reads it at runtime via `importlib.metadata`.
- `docs/source/conf.py` reads it the same way.

**Documentation**
- `dev_scripts/README.md` — comprehensive maintainer guide covering CI,
  the release workflow, PyPI setup, and keeping Python versions current.
- `docs/source/release.rst` — overview for the docs site.

---

## What still needs to be done

### 1. Configure PyPI Trusted Publishing (one-time, blocking for PyPI upload)

`publish.yml` is written and ready.  The matching configuration on the
PyPI side has not yet been set up.  Until it is, `publish.yml` will fail
at the upload step (but nothing else is affected — the draft release and
wheel builds work fine).

Steps:
1. Log in to pypi.org as a project maintainer.
2. Go to the svmbir project → **Publishing** tab → **Add a new publisher**.
3. Fill in: Owner `cabouman`, Repository `svmbir`, Workflow `publish.yml`.
4. No environment constraint is needed.

### 2. Cut the real release

The dry run (`test_release.sh`) was run successfully and all 16 assets
were verified.  The current version in `pyproject.toml` is `0.4.0`.

Run from the `prerelease` branch, inside `dev_scripts/`:

```bash
git checkout prerelease && git pull

# One-time machine setup (if not already done):
./install_python_frameworks.sh   # installs Python.org framework builds for cibuildwheel
# gh auth login                  # if gh CLI not yet authenticated

./cut_release.sh                 # prompts for new version (e.g. 0.4.1)
./test_pypi.sh v0.4.1            # test-install from draft release assets

gh pr create --base master --title "Release v0.4.1"
# Wait for CI to pass, then merge the PR.
# Then: go to the GitHub release page and click "Publish release"
#       — this triggers automatic PyPI upload via publish.yml.
```

### 3. Dependabot alerts

GitHub has flagged 6 vulnerabilities on the repo (2 critical, 2 high,
2 moderate): https://github.com/cabouman/svmbir/security/dependabot

These are likely in GitHub Actions action pins or docs tooling — not in
the package itself — but they should be reviewed before merging to master.

---

## Key design decisions

- **macOS wheels built locally**, not on GitHub Actions.  macOS runners had
  17-hour queue times; local cibuildwheel + delocate is faster and fully
  portable.  `build_mac_wheels.sh` requires a machine with Apple Silicon,
  the Python.org framework installs, and an authenticated `gh` CLI.

- **Draft releases as the coordination point**.  GitHub Actions creates the
  draft on tag push.  The Linux job and the local mac script both upload to
  it.  The developer publishes when satisfied with all 16 assets.

- **PyPI Trusted Publishing (OIDC)**.  No API token stored anywhere.  The
  `publish.yml` workflow filename is the identifier; it must match exactly
  what is registered on pypi.org.

- **`git push origin "$TAG"`** (not `git push --tags`).  `--tags` pushes
  every local tag and caused a bug in an earlier version of the scripts.

- **bash 3.2 compatibility**.  macOS ships `/bin/bash` as bash 3.2.  Do
  not use complex `'"$VAR"'` quoting inside `trap` bodies — use named
  functions instead.  This was a real bug that caused a spurious "command
  not found" error at the end of `test_release.sh`.
