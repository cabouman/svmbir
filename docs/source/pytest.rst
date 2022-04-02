==============
Running pytest
==============

From a clean repository, build and run unit tests with the following::

    $ CC=gcc python setup.py build_ext --inplace
    $ pytest
  
This should be repeated for each supported compiler and platform.
