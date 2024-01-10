======================
Upload package to PyPI
======================

This is only relevant for registered maintainers.

Prior to this stage, make sure to complete all the 
steps for `preparing the release <release.html>`_ .


Set up environment and build distribution files
-----------------------------------------------

Run::

    $ conda create --name svmbir_pypi python=3.10
    $ conda activate svmbir_pypi
    $ pip install -r requirements.txt
    $ CC=gcc python setup.py sdist bdist_wheel

Use gcc here for the binary distribution. For now other supported compilers
will require the user to install the package from source.


Delocate wheel files (macOS/x86_64 builds only)
-----------------------------------------------

This only applies to building wheels for pre-M1 macs.
``delocate-wheel`` will generate a fixed wheel by including more widely compatible dylib files with the package.
Run the following command on an older mac version like 10.14 for the widest compatibility::

    $ pip install delocate
    $ cd dist
    $ delocate-wheel -w fixed_wheels -v <svmbir-xxxxx>.whl    # update wheel file name


Upload to TestPyPI and test installation
----------------------------------------

This is only available for registered maintainers.
If granted, you need to be registered in testpypi,
and for authentication you'll need to add API tokens from Account Settings.

 1. Upload to testpypi. NOTE you cannot upload same version more than once::

    $ pip install twine
    $ python -m twine upload --repository testpypi dist/*

 View the package upload here:
 `https://test.pypi.org/project/svmbir <https://test.pypi.org/project/svmbir>`__

 2. Test the uploaded package::

    $ pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple svmbir==0.2.10  # change version no.
    $ python -c "import svmbir"     # spin the wheel

 3. Run one of the `demo scripts <examples.html>`_

 NOTE: If the install fails and you need to re-test, TEMPORARILY set the version
 number in setup.py from X.X.X to X.X.X.1 (then 2,3,etc.), for further testing.
 After the test is successful, merge any require changes into the master branch,
 re-set the version number in setup.py, delete and re-create the git tag,
 and proceed to PyPI upload.

Upload to PyPI and test installation
----------------------------------------

This is only available for registered maintainers.
If granted, you need to be registered in pypi,
and for authentication you'll need to add API tokens from Account Settings.

 1. Upload to pypi. NOTE you cannot upload same version more than once::

    $ pip install twine
    $ python -m twine upload dist/*

 View the package upload here:
 `https://pypi.org/project/svmbir <https://pypi.org/project/svmbir>`__

 2. Test the uploaded package::

    $ pip install svmbir    # OR, "svmbir==0.2.10" e.g. for a specific version number
    $ python -c "import svmbir"     # spin the wheel

 3. Run one of the `demo scripts <examples.html>`_


Reference
---------
More details can be found in the sources below.

  | [1] Packaging Python projects `[link] <https://packaging.python.org/tutorials/packaging-projects/>`__
  | [2] Using TestPyPI `[link] <https://packaging.python.org/guides/using-testpypi/>`__
