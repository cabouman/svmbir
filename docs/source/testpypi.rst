========================
Test package in testpypi
========================

Use Testpypi in MacOS.
----------------------

Before distributing to pypi, we should first test those packages in testpypi.

Developer can follow following instruction to upload package to testpypi

 1. Register in testpypi.

 2. In Account setting, Click Add API tokens.
    Follow testpypi's instruction and copy tokens to set up ypur local computer.

 3. Include necessary files in MANIFEST.in.

 4. Include setup.py required packages in pyproject.toml.

 5. Build distribution archives

    ``pip install -r requirements.txt``

    ``CC=gcc python3 setup.py sdist bdist_wheel``

    Compilers other than gcc can also be used.

 6. Upload the distribution archives

    ``pip install setuptools twine``

    ``python3 -m twine upload --repository testpypi dist/*``

 7. Create a clean envrionment and download the distribution archives


    ``CC=gcc pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple svmbir==1.2.6.0``

    Compilers other than gcc can also be used.

Reference
---------
More details can be found in below reference webpages.

[1] Packaging Python Projects. `[here] <https://packaging.python.org/tutorials/packaging-projects/>`_

[2] Using TestPyPI. `[here] <https://packaging.python.org/guides/using-testpypi/>`_
