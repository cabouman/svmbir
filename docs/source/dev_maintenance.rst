.. _DevMaintenanceDocs:

===================
Package Maintenance
===================

Unit Tests
----------

From the top repository folder, build the package and run the unit tests
with::

    $ pip install -e ".[dev]"
    $ pytest

The suite runs in a few seconds.  CI runs it on Linux for every supported
Python version, and on macOS for one, on each push to ``main`` or
``prerelease``.

Building the Documentation
--------------------------

Install svmbir with its docs dependencies, then build the HTML::

    $ pip install -e ".[docs]"
    $ cd docs
    $ SVMBIR_BUILD_DOCS=true make html

The HTML files are written to ``docs/build/html``; open ``index.html`` to
review them.  Read the Docs builds the same way from ``.readthedocs.yaml``
in the repository root, which installs the package with its docs
dependencies from ``pyproject.toml``.  The ``latest`` version tracks
``main`` and the ``prerelease`` version tracks ``prerelease``.

Clean Reinstall
---------------

The scripts in ``dev_scripts`` rebuild the ``svmbir`` conda environment
from nothing.  Run them from inside ``dev_scripts``::

    $ source clean_install_all.sh

This removes the ``svmbir`` conda environment, recreates it, installs the
package with its development, docs, and demo dependencies, and builds the
documentation.  The individual steps are ``clean_svmbir.sh``,
``install_conda_environment.sh``, ``install_svmbir.sh``, and
``install_docs.sh``.

Preparing a New Release
-----------------------

Only a small number of dedicated maintainers should cut releases.  The
scripts named below are in ``dev_scripts`` and print what to do next as they
run.

Branching model
+++++++++++++++

All development happens on feature branches that are merged into
``prerelease`` via pull request.  CI (automated testing on Linux across
all supported Python versions) runs on every PR.  Once a release is
ready, ``prerelease`` is merged into ``main`` via a second PR, also
gated by CI.  The ``main`` branch always reflects the latest published
release.

Release artifacts
+++++++++++++++++

Each release produces Linux x86_64 wheels, macOS arm64 wheels, and a source
distribution, one wheel per supported Python version.  GitHub Actions
builds and tests all of them when a version tag is pushed
(``release.yml``) and attaches them to a draft GitHub release.  Publishing
the draft uploads them to PyPI (``publish.yml``).

Release process
+++++++++++++++

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
++++++++++++++++++++++++++++++

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
++++++++++++++++++++++++++++++++

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
