=======================
Preparing a new release
=======================

Only a small number of dedicated maintainers should cut releases.
This page gives an overview of the process; the step-by-step details
are in ``dev_scripts/README.md`` in the repository.

Branching model
---------------

All development happens on feature branches that are merged into
``prerelease`` via pull request.  CI (automated testing on Linux across
all supported Python versions) runs on every PR.  Once a release is
ready, ``prerelease`` is merged into ``master`` via a second PR, also
gated by CI.  The ``master`` branch always reflects the latest published
release.

Release artifacts
-----------------

Each release produces:

* **Linux wheels** (x86_64 and i686, all supported Python versions) —
  built automatically by GitHub Actions (``release.yml``) when a version
  tag is pushed.
* **macOS arm64 wheels** (all supported Python versions) — built locally
  on a developer machine using ``cibuildwheel`` and uploaded to the same
  draft GitHub Release.
* **Source distribution** (``sdist``) — built by GitHub Actions alongside
  the Linux wheels.

All artifacts are collected in a draft GitHub Release and verified before
anything is published publicly.

Release process summary
-----------------------

Prerequisites (one-time setup per machine):

* Run ``dev_scripts/install_conda_environment.sh`` to create the ``svmbir``
  conda environment, which installs ``cibuildwheel`` and the ``gh`` CLI.
* Run ``dev_scripts/install_python_frameworks.sh`` to install the official
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
   release on GitHub (1 macOS arm64 + 2 Linux wheels per Python version,
   plus 1 sdist).

4. **Optional test-install**: ``./test_pypi.sh v<version>`` downloads the
   release assets and installs them into a clean conda environment to run
   pytest before anything goes public.

5. **Merge**: open a PR from ``prerelease`` to ``master`` and merge after
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

See ``dev_scripts/README.md`` for instructions on adding new Python
versions (each October) and dropping end-of-life versions.  The key
files to keep in sync are ``ci.yml``, ``pyproject.toml`` (``build``
setting and ``requires-python``), and ``install_python_frameworks.sh``.
