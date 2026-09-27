============
Installation 
============

The **svmbir** package is available from conda-forge, PyPI, or can be built and installed from source.


Installing from conda-forge
---------------------------

.. _virt env:

1. Create and activate a clean virtual environment (optional, but recommended)::

    conda create --name svmbir python=3.10
    conda activate svmbir

2. Install from the conda-forge channel::

    conda install -c conda-forge svmbir

  To list all of the versions of svmbir available on the target platform::

    conda search -c conda-forge svmbir



Installing from PyPI
--------------------

1. Create and activate a clean virtual environment (recommended, see :ref:`above<virt env>`)

2. Install from PyPI::

    pip install svmbir

  **Note**:
  If installing on an older platform, it's possible the wheel installation will fail.
  A possible remedy is to install from the package source distribution on PyPI with the following command::

    pip install --no-binary svmbir svmbir

  However note this requires having GNU/gcc and OpenMP libraries installed on the target platform.

  Other may-be-useful commands::

    pip install svmbir --upgrade    # upgrade existing installation
    pip install svmbir==<ver_no>    # install specific version
    pip index versions svmbir       # list available versions on pypi.org


Build and install from source
-----------------------------

This method requires a compatible C compiler (GNU/gcc, Intel/icc) and OpenMP libraries.
Some additional platform-specific notes are given below.

1. Download source code from Github::

    git clone --recursive https://github.com/cabouman/svmbir.git
    cd svmbir

  This will download the python source code along with the **sv-mbirct** C-code submodule.
  **Do not** use the Github "Download" link to download the repository because this
  zip container will not include the C-code submodule.

2. Create and activate a clean virtual environment (recommended, see :ref:`above<virt env>`)

3. Install dependencies, build extension, install::

    # Run in the top repository folder
    pip install .

  On Linux this uses ``gcc``; on MacOS it uses ``clang`` and needs the OpenMP library
  (see the notes below).  Set ``CC=icc`` to build with the Intel compiler on Linux.


Additional Notes on source installation
---------------------------------------

1. **Intel icc Compiler:**
The Intel compiler and OMP libraries when coupled with appropriate Intel x86_64 processors
can substantially increase ``svmbir`` performance through better optimization and enabling vector instructions.
The Intel compiler and libraries for Linux, Windows, and MacOS are freely available from Intel,
but not always easy to install.

2. **Installation on MacOS:**
``svmbir`` builds on MacOS with the ``clang`` compiler from the Xcode Command Line Tools
plus the OpenMP library, which Apple does not ship.  Install both, then build::

    xcode-select --install
    conda install -c conda-forge llvm-openmp
    pip install .

The ``CC`` variable is not needed on MacOS.  Setting ``CC=gcc`` is ignored, because
Homebrew gcc produces x86_64 binaries on Apple Silicon machines.  If the OpenMP
library is missing, the build stops with a message that says how to install it.

3. **Installation on Linux:**
``svmbir`` builds on Linux with ``gcc`` and its OpenMP library, which most Linux
distributions install with the compiler.  Build with::

    pip install .


4. **Windows Installation:**
It's possible to install svmbir in Windows OS in experimental cases, but there are not the resources 
nor test platforms available for us to widely support Windows installations.
The following configuration has been observed to work:

* *64-bit gcc or Intel icc compiler:* In most applications you'll want a 64-bit compiler such as `[MinGW-w64/GCC] <http://winlibs.com>`__ or the Intel/ICC compiler as described above.  Commonly available Windows gcc compilers are only 32-bit and will result in ``calloc`` errors when working with array sizes greater than 2GB.

* *MinGW + MSYS environment:* Recommend installing ``MinGW`` including the ``msys`` utilities. These utilities support a minimalist set of traditional UNIX tools.

* *Git Bash:* Recommend installing `[Git Bash] <https://gitforwindows.org>`__ to support bash scripting.

