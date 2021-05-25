===============================
Build documentation with Sphinx
===============================

Build HTML locally
------------------

1. Go to the docs folder

	``cd docs``

2. Install sphinx dependencies if they're not already

	``pip install -r requirements.txt``

  The documentation contains a Jupyter Notebook example which will require Pandoc.
  If the build in the next step fails Pandoc will have to be
  `[installed] <https://pandoc.org/installing.html>`__.
  On a Mac with Homebrew, run ``brew install pandoc`` .

3. Build HTML files

	``SVMBIR_BUILD_DOCS=true make html``

If the build was successful, the HTML files will be in the build/html folder.
Open index.html to review the documentation.

Build HTML in readthedocs
-------------------------

1. Register in readthedocs.
2. Import your project from GitHub.
3. Click in your project, click Admin section below your project's name.
4. Click advanced setting, in Default settings. Put docs/requirements.txt to Requirements file. Enable "Install Project".
