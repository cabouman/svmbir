===============================
Build documentation with Sphinx
===============================

Build HTML locally
------------------

1. Install svmbir with its docs dependencies.
   To do this, go to the package root directory and run::

    $ pip install -e ".[docs]"

2. Then go to the docs folder::

    $ cd docs

3. Build HTML files::

    $ SVMBIR_BUILD_DOCS=true make html

If the build was successful, the HTML files will be in the svmbir/docs/build/html folder.
Open index.html to review the documentation.

Build HTML in readthedocs
-------------------------

1. Register in readthedocs.
2. Import your project from GitHub.
3. The build is configured by ``.readthedocs.yaml`` in the repository root, which installs
   the package with its docs dependencies from ``pyproject.toml``.
