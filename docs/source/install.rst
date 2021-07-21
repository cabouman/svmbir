============
Installation 
============

The ``svmbir`` package is available from PyPI, or can be built from source.
Currently, the PyPI installation will only build using a gcc compiler.
If other high performance compilers are desired, the package needs to
be built from source.

Install through PyPI
-----------------------------------------
In order to install from PyPI, you **must first install the gcc compiler**.

Instructions on how to install gcc on a Mac are listed :ref:`below <Mac gcc>`.
Remember, the default macOS compiler, clang, will appear as gcc even though it is not gcc.
So in order to double check that you are getting the correct compiler, you should first run the command ``gcc --version``.

In order to install using PyPI, run the following commands:


1. Create a Virtual Environment (optional)

  It is recommended that you install to a virtual environment.
  If you have Anaconda installed, you can run the following:

	| ``conda create --name svmbir python=3.8``
	| ``conda activate svmbir``


2. Install from PyPI

	``pip install svmbir``

  If a wheel is available for your platform, this will install the binaries to your system.
  If not available, this will build from source files in which case a standard gcc compiler
  needs to be available on your system.


Downloading and installing from source
-----------------------------------------

1. Download the source code:

  In order to download the C and python code, move to a directory of your choice and run the following two commands.

	| ``git clone --recursive https://github.com/cabouman/svmbir.git``
	| ``cd svmbir``

  This will download the python source code along with the ``sv-mbirct`` C-code submodule.
  *Warning: Do not* use the github "Download" link to download the repository because the
  zip container will likely not include the C-code submodule.

2. Create a Virtual Environment:

  It is recommended that you install to a virtual environment.
  If you have Anaconda installed, you can run the following:

	| ``conda create --name svmbir python=3.8``
	| ``conda activate svmbir``

  Install the dependencies using:

	``pip install -r requirements.txt``

  Before using the package, this ``svmbir`` environment needs to be activated.


3. Install:

The ``svmbir`` package requires a C compiler together with OpenMP libraries for parallel multicore processing.
The four supported compilers are the open source ``gcc`` compiler, Microsoft Visual C ``msvc``, Intel's ``icc`` compiler, or the Apple's ``clang`` compiler.
The Intel compiler currently offers the best performance on x86 processors through the support of the AVX instruction set;
however, the ``gcc`` and ``clang`` compilers are often more readily available.

**Important:** You must first install one of these compilers together with the associated OpenMP libraries on your computer.
MacOS and Windows users should refer to the instructions :ref:`below <Windows and Mac>` for more details on installation of the compilers, OMP libraries and associated utilities.

Once the compiler and OMP libraries are installed, the following commands can be used to compile the ``svmbir`` code.

For installation using the four possible compiler options, run one of the following in a bash shell:

``CC=gcc pip install .``

``CC=icc pip install .``

``CC=clang pip install .``

``CC=msvc pip install .``

In each case, the commands should be run from the root directory of the repository.
Also, see the sections below for trouble shooting tips for installing under the different operating systems.

You can verify the installation by running ``pip show svmbir``, which should display a brief summary of the packages installed in the ``svmbir`` environment.
Now you will be able to use the ``svmbir`` python commands from any directory by running the python command ``import svmbir``.



.. _Windows and Mac:

Installation on Windows and MacOS
---------------------------------

Below are some tips for compiling and running the package under the Windows and MacOSx operating systems.
Linux is more straight forward.

**1. Intel icc Compiler:**
The Intel compiler and OMP libraries when coupled with the appropriate Intel x86 processor
can substantially increase ``svmbir`` performance by enabling the AVX2 instructor set.
The ``icc/OpenMP`` compiler and libraries exists for Linux, Windows, and MacOS, but may need to be purchased.
The icc compiler is available `[here] <https://software.intel.com/content/www/us/en/develop/tools/parallel-studio-xe.html>`__.


**2. Windows Installation:**
The package will run under Windows, but there tend to be more things that can go wrong due to the wide variety of possible configurations. The following list of recommended configurations have been tested to work, but others are possible:

* *64-bit gcc or Intel icc compiler:* For the command line version, make sure to install a 64bit compiler such as the ``MinGW_64`` available from `[here] <http://winlibs.com>`__ or the Intel ``icc`` compiler as described above. Commonly used gcc compilers are only 32bit and will create ``calloc`` errors when addressing array sizes greater than 2Gb.

* *MinGW + MSYS environment:* For the command line version, we recommend installing ``MinGW`` including the ``msys`` utilities. These utilities support a minimalist set of traditional UNIX tools.

* *Git Bash:* We recommend installing `[Git Bash] <https://gitforwindows.org>`__ to support bash scripting.

One known issue is that in some Windows bash environments the C executable ``mbir_ct.exe`` may not be properly moved to the ``bin`` directory.
If this occurs, then the problem can be resolved by manually moving the file.


.. _Mac gcc:

**3. Installation of gcc on MacOS:**
If you are installing from PyPI, then we recommend you use the gcc compiler.
In order to install gcc, you should do the following:

* Install the ``Command Line Tools for Xcode`` available `[here] <https://developer.apple.com/download/more/>`__.

* Install Homebrew from `[here] <https://brew.sh>`__. This is the package manager that can be used to install gcc on a mac.

* Use Homebrew to install gcc using the command ``brew install gcc``. This will also install the OMP libraries.

* Create a symbolic link in /usr/local/bin that maps “gcc” to “gcc-10”, or the most current compiler. To do this, do the following command:

    ``ln -sf /usr/local/bin/gcc-10 /usr/local/bin/gcc``

    You can also check the contents of /usr/local/bin to make sure you link to the most current version of gcc that you installed.

* Finally, check that you are getting the correct compiler by using the command:

    ``gcc --version``



.. _Mac clang:

**4. Installation of clang on MacOS:**
Some MacOS users use the ``clang`` compiler provided as part of the Xcode Developer Tools.
However, this is not recommended for PyPI installation.
In this case, the ``gcc`` command in the MacOS environment is **not** actually ``gcc``.
Instead it is an alias to the ``clang`` compiler.
Therefore, the C code should be compiled using the ``clang`` option.

In order to obtain ``clang`` you will need to install the most up-to-date version of both Xcode
and ``Command Line Tools for Xcode`` available `[here] <https://developer.apple.com/download/more/>`__.

Importantly, the Xcode Developer tools **do not include** the required OpenMP libraries.
The OMP libraries can be obtained from `[here] <https://mac.r-project.org/openmp/>`__.
You will need to download a file of the form ``openmp-XXX.tar.gz``.
The tar file will contain the following files:

    ```
    /usr/local/lib/libomp.dylib
    ```
    ```
    /usr/local/include/ompt.h
    ```
    ```
    /usr/local/include/omp.h
    ```
    ```
    /usr/local/include/omp-tools.h
    ```

These files should be moved to the specified directories.
You may also need to open the file ``/usr/local/lib/libomp.dylib``.
This will generate a splash screen that requests permision of OSx to execute the library.

In addition, after OS updates, you may need to reinstall the Xcode toolkit using the command: ``xcode-select --install``


**5. Compile C-Code (Legacy Instructions):**

This section includes information on how to compile the code for the CMD_LINE interface. This is an older legacy version of the code.
So it is not needed for most users.

The ``svmbir`` package requires a C compiler together with the OpenMP libraries for parallel multicore processing.
The three supported compilers are the open source ``gcc`` compiler, Intel's ``icc`` compiler, or the Apple's ``clang`` compiler.
The Intel compiler currently offers the best performance on x86 processors through the support of the AVX instruction set;
however, the ``gcc`` and ``clang`` compilers are often more readily available.

**Important:** You must first install one of these three compilers together with the associated OpenMP libraries on your computer.
MacOS and Windows users should refer to the instructions :ref:`below <Windows and Mac>` for more details on installation of the compilers, OMP libraries and associated utilities.

Once the compiler and OMP libraries are installed, the following commands can be used to compile the ``svmbir`` code.

For ``gcc`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=gcc``

For ``icc`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=icc``

For ``clang`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=clang``

In each case, the commands should be run from the root directory of the repository.
Also, see the sections below for trouble shooting tips for installing under the different operating systems.
