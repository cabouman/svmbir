=======================
Preparing a new release
=======================

Only a small number of dedicated maintainers should cut releases.
This page describes the process.  The scripts named below are in
``dev_scripts`` and print what to do next as they run.

Branching model
---------------

All development happens on feature branches that are merged into
``prerelease`` via pull request.  CI (automated testing on Linux across
all supported Python versions) runs on every PR.  Once a release is
ready, ``prerelease`` is merged into ``main`` via a second PR, also
gated by CI.  The ``main`` branch always reflects the latest published
release.

Release artifacts
-----------------

Each release produces:

* **Linux wheels** (x86_64, all supported Python versions) —
  built automatically by GitHub Actions (``release.yml``) when a version
  tag is pushed.
* **macOS arm64 wheels** (all supported Python versions) — built by
  GitHub Actions on an Apple Silicon runner, in the same workflow.
  ``dev_scripts/build_mac_wheels.sh`` remains as a manual fallback.
* **Source distribution** (``sdist``) — built by GitHub Actions alongside
  the Linux wheels.

All artifacts are collected in a draft GitHub Release and verified before
anything is published publicly.

Release process summary
-----------------------

Prerequisites (one-time setup per machine):

* Run ``dev_scripts/install_conda_environment.sh`` to create the ``svmbir``
  conda environment, which installs ``cibuildwheel`` and the ``gh`` CLI.
* Only for the manual macOS fallback: run
  ``dev_scripts/install_python_frameworks.sh`` to install the official
  Python.org framework builds required by ``cibuildwheel``.
* Run ``gh auth login`` once to authenticate the ``gh`` CLI with GitHub.
* Configure PyPI Trusted Publishing once (see below).

The release sequence (all scripts run from ``dev_scripts/`` on the
``prerelease`` branch):

1. **Dry run**: ``./test_release.sh`` — creates a throwaway ``-bump-test``
   tag, builds all wheels, lets you verify the draft release, then cleans
   everything up automatically.

2. **Cut the release**: ``./cut_release.sh`` — bumps the version in
   ``pyproject.toml``, commits, tags, and triggers the full build.
   Prompts you through each step.

3. **Verify**: confirm all wheels and the sdist are attached to the draft
   release on GitHub (1 macOS arm64 + 1 Linux x86_64 wheel per Python version,
   plus 1 sdist).

4. **Optional test-install**: ``./test_pypi.sh v<version>`` downloads the
   release assets and installs them into a clean conda environment to run
   pytest before anything goes public.

5. **Merge**: open a PR from ``prerelease`` to ``main`` and merge after
   CI passes.

6. **Publish**: click "Publish release" on the GitHub draft release page.
   This triggers ``publish.yml``, which automatically uploads all wheels
   and the sdist to PyPI.

PyPI Trusted Publishing setup
------------------------------

Releases are published to PyPI automatically via GitHub Actions using
`Trusted Publishing`_ (OIDC — no stored API token required).  This is a
one-time configuration:

1. Log in to `pypi.org`_ and navigate to the svmbir project.
2. Go to **Publishing** → **Add a new publisher**.
3. Set: Owner = ``cabouman``, Repository = ``svmbir``,
   Workflow = ``publish.yml``.
4. No environment constraint is needed.

Once configured, publishing to PyPI happens automatically whenever a
GitHub Release is published — no further action required.

.. _Trusted Publishing: https://docs.pypi.org/trusted-publishers/
.. _pypi.org: https://pypi.org/project/svmbir/

Updating Python version support
--------------------------------

Python ships a new version each October, and versions reach end of life
about five years after release.  The supported versions are listed in
three places that must agree:

* ``python-version`` in ``.github/workflows/ci.yml`` (the CI matrix);
* ``build`` under ``[tool.cibuildwheel]`` in ``pyproject.toml`` (the
  wheels that a release builds);
* ``requires-python`` in ``pyproject.toml`` (the oldest version allowed).

To add a version, add it to the first two lists.  Cython can lag a new
Python release by a few months; if CI fails on the new version with a
Cython build error, remove it again and retry after the next Cython
release.  To drop a version, remove it from the first two lists and
raise ``requires-python``.  The manual macOS fallback script
``install_python_frameworks.sh`` has its own version list at the top.
