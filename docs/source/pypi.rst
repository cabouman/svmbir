======================
Upload package to PyPI
======================

Summary
-------

The general procedure for releasing a new version to PyPI is,

 1. Complete all the preliminary steps for `preparing the release <release.html>`_

 2. Set up a conda environment with the required tools

 3. Build the binary and source distribution

 4. Upload the release to TestPyPI, and test installation from TestPyPI

 5. Upload the release to PyPI, and test installation from PyPI

There are two files included with the repository that are specific to PyPI:
MANIFEST.in and pyproject.toml.


Set up environment
------------------

In addition to the standard svmbir requirements, two additional packages are needed
for the build and upload.

    | ``conda create --name svmbir_pypi python=3.8``
    | ``conda activate svmbir_pypi``
    | ``pip install -r requirements.txt``
    | ``pip install setuptools twine``


Build distribution files
------------------------

    ``CC=gcc python setup.py sdist bdist_wheel``

    Use gcc here for the binary distribution. For now other supported compilers
    will require the user to install the package from source.


Upload to TestPyPI and test installation
----------------------------------------

 Before this you'll need to be registered in testpypi, and be granted access as a
 maintainer of the project.
 For authentication, you'll also need to add API tokens from Account Settings.

 1. Upload the package to testpypi. NOTE you cannot upload same version more than once.

	``python -m twine upload --repository testpypi dist/*``

    View the package upload here:
    `https://test.pypi.org/project/svmbir/0.2.0/ <https://test.pypi.org/project/svmbir/>`__ (add version no.)

 2. Create a clean environment and install the package

  | ``conda create --name svmbir_temp python=3.8``
  | ``conda activate svmbir_temp``
  | ``pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple svmbir==0.2.0`` (change version no.)

 3. Check the installation

	| ``conda list | grep svmbir``
	| ``python -c "import svmbir"``

 4. Run one of the `demo scripts <https://github.com/cabouman/svmbir/tree/master/demo>`_

 5. Remove temporary environment

	| ``conda deactivate``
	| ``conda remove --name svmbir_temp --all``

 NOTE: If the install fails and you need to re-test, TEMPORARILY set the version
 number in setup.py from X.X.X to X.X.X.1 (then 2,3,etc.), for further testing.
 After the test is successful, merge any require changes into the master branch,
 re-set the version number in setup.py, delete and re-create the git tag,
 and proceed to PyPI upload.

Upload to PyPI and test installation
----------------------------------------

 Before this you'll need to be registered in pypi, and be granted access as a
 maintainer of the project.
 For authentication, you'll also need to add API tokens from Account Settings.


 1. Upload package to pypi. NOTE you cannot upload same version more than once.

	``python -m twine upload dist/*``

    View the package upload here: `<https://pypi.org/project/svmbir/>`_

 2. Create a clean environment and install the package

	| ``conda create --name svmbir_temp python=3.8``
	| ``conda activate svmbir_temp``
	| ``pip install svmbir``
	| OR ``pip install svmbir==0.2.0`` for a specific version number

 3. Check the installation

	| ``conda list | grep svmbir``
	| ``python -c "import svmbir"``

 4. Run one of the `demo scripts <https://github.com/cabouman/svmbir/tree/master/demo>`_

 5. Remove temporary environment

	| ``conda deactivate``
	| ``conda remove --name svmbir_temp --all``


Reference
---------
More details can be found in the sources below.

  | [1] Packaging Python projects `[link] <https://packaging.python.org/tutorials/packaging-projects/>`__
  | [2] Using TestPyPI `[link] <https://packaging.python.org/guides/using-testpypi/>`__
