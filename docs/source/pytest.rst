==============
Running pytest
==============

From the top repository folder, build the package and run the unit tests with::

    $ pip install -e ".[dev]"
    $ pytest

CI runs the tests on Linux for every supported Python version on each push to
``main`` or ``prerelease``.
