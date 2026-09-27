.. _DevMaintenanceDocs:

===================
Package Maintenance
===================

Tests
-----

From the top repository folder::

    pip install -e ".[dev]"
    pytest

CI runs the same tests on every push to ``main`` or ``prerelease``.

Documentation
-------------

From the top repository folder::

    pip install -e ".[docs]"
    cd docs
    SVMBIR_BUILD_DOCS=true make html

Open ``docs/build/html/index.html``.  Read the Docs builds ``latest`` from
``main`` and ``prerelease`` from ``prerelease``.

Release
-------

Work goes to ``prerelease``; ``main`` holds the last release.  A release
takes three steps.  The first needs the ``gh`` command, logged in.

1. From ``prerelease``, with CI passing::

       dev_scripts/release.sh 0.X.Y

   This sets the version, tags the commit, and opens the pull request to
   ``main``.  GitHub builds the wheels into a draft release.

2. On GitHub, merge the pull request when its checks pass.

3. On GitHub, open the draft release ``v0.X.Y`` and click **Publish
   release**.  The wheels go to PyPI.

If a wheel build fails, fix it on ``prerelease``, delete the tag and the
draft release on GitHub, and repeat step 1.

conda-forge
-----------

conda-forge builds its own package from the PyPI source.  Within a day of a
release, a robot opens a pull request on
`conda-forge/svmbir-feedstock <https://github.com/conda-forge/svmbir-feedstock>`_.
Check that its recipe still matches ``pyproject.toml``, wait for its checks,
and merge.  Merge its pull requests for new Python versions the same way.

Once only
---------

* **PyPI:** on pypi.org, in the svmbir project, under Publishing, add a
  publisher with owner ``cabouman``, repository ``svmbir``, workflow
  ``publish.yml``.  Releases then upload without a stored token.
* **New Python version:** add it to ``python-version`` in
  ``.github/workflows/ci.yml`` and to ``build`` in ``pyproject.toml``.
  Drop old versions there and raise ``requires-python``.
* **Clean reinstall** of the ``svmbir`` conda environment::

      cd dev_scripts
      source clean_install_all.sh
