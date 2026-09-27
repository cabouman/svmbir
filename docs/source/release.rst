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

Each release produces Linux x86_64 wheels, macOS arm64 wheels, and a source
distribution, one wheel per supported Python version.  GitHub Actions
builds and tests all of them when a version tag is pushed
(``release.yml``) and attaches them to a draft GitHub release.  Publishing
the draft uploads them to PyPI (``publish.yml``).

Release process
---------------

The release takes three steps.  The first needs the ``gh`` command, logged
in to GitHub.  The example below releases version 0.X.Y.

1. Start the release, from the ``prerelease`` branch with a clean working
   tree and CI passing on the current commit::

       dev_scripts/release.sh 0.X.Y

   What this does:

   * Sets the version in ``pyproject.toml`` to 0.X.Y, commits, and pushes
     to ``prerelease``.
   * Tags the commit ``v0.X.Y`` and pushes the tag.  GitHub Actions builds
     the wheels and the sdist and attaches them to a draft release.
   * Opens the pull request from ``prerelease`` to ``main``.

2. On GitHub, when the checks pass, merge the pull request.

3. On GitHub, open the draft release ``v0.X.Y`` under Releases, check that
   the wheels and the sdist are attached, and click **Publish release**.
   GitHub Actions uploads them to PyPI.  Check with::

       pip index versions svmbir

If the wheel build fails, fix the problem on ``prerelease``, delete the tag
and the draft release on GitHub, and run step 1 again.

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
raise ``requires-python``.
