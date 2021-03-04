===============================
Build documentation with sphnix
===============================

Build HTML locally
------------------

1. Go to docs folder.

	``cd docs``

2. Install sphnix dependencies.

	``pip install -r docs/requirements.txt``

3. Build HTML automatically.

	``SVMBIR_BUILD_DOCS=true make html``

4. Check HTML.

	``cd build/html``

If build successfully, html files will be in build folder.
Click index.html and go to API reference to see if everything works good.

Build HTML in readthedoc
------------------------

1. Register in readthedocs.
2. Import your project from GitHub.
3. Click in your project, click Admin section below your project's name.
4. Click advanced setting, in Default settings. Put docs/requirements.txt to Requirements file. Enable "Install Project".
