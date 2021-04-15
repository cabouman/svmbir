======================
Upload package to PyPI
======================

Upload package to PyPI with MacOS
---------------------------------

Developer can follow following instruction to upload package to PyPI

 1. Change to svmbir directory.

    - Check out the version to be released.

    - Update version number in setup.py if needed. (You cannot upload same version twice.)

 2. Create conda environment.

    ``conda create -n svmbir_pypi python=3.8``

    ``conda activate svmbir_pypi``

    ``pip install -r requirements.txt``

    ``pip install setuptools twine``

 3. Build package.

    ``CC=gcc python setup.py sdist bdist_wheel``

 4. Upload package to pypi.

    ``python -m twine upload dist/*``


 5. Testing

    - View pypi webpage `[here] <https://pypi.org/project/svmbir/>`_

    - Try to install through PyPI.

    ``pip install svmbir``
