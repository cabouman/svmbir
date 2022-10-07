===============================
Build documentation with Sphinx
===============================

Build HTML locally
------------------

1. Make sure the svmbir dependencies are installed in your conda environment.
   To do this, go to the package root directory and run::

    $ pip install -r requirements.txt

2. Then go to the docs folder::

    $ cd docs

3. Install sphinx dependencies::

    $ pip install -r requirements.txt

  The documentation contains a Jupyter Notebook example which will require Pandoc.
  If the build in the next step fails Pandoc will have to be
  `[installed] <https://pandoc.org/installing.html>`__.
  On a Mac with Homebrew, run ``brew install pandoc`` .

4. Build HTML files::

    $ SVMBIR_BUILD_DOCS=true make html

If the build was successful, the HTML files will be in the svmbir/docs/build/html folder.
Open index.html to review the documentation.

Build HTML in readthedocs
-------------------------

1. Register in readthedocs.
2. Import your project from GitHub.
3. Click in your project, click Admin section below your project's name.
4. Click advanced setting, in Default settings. Put docs/requirements.txt to Requirements file. Enable "Install Project".
