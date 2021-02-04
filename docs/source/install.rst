============
Installation 
============

This section covers the basics of how to download and install svmbir.
At this time, the ``svmbir`` package must be built from source.
In the future, we also plan to make it installable from ``PyPI`` or ``Conda``.


Downloading and Installing svmbir Package
-----------------------------------------

1. *Download code:*
In order to download the C and python code, move to a directory of your choice and run the following two commands.

``git clone --recursive https://github.com/cabouman/svmbir.git``

``cd svmbir``

This first command recursively downloads a folder containing the svmbir python wrapper along with the ``sv-mbirct`` C-code submodule,
and the second command moves into the root directory of the repository.
*Warning: Do not* used standard GUI methods to clone the repository because they may not recursively copy the C-code submodule. 


2. *Create a Virtual Environment:*

It is recommended that you create a conda environment.
To do this, first install ``Anaconda``, and then create and activate an ``svmbir`` environment using the following two commands.

``conda create -n svmbir python=3.8``

``conda activate svmbir``

This will create an empty conda environment.

Install dependencies using:

``pip install -r requirements.txt``

Before running the code, this ``svmbir`` conda environment should always be activated.


3. *Install:*

The ``svmbir`` package requires a C compiler together with the OpenMP libraries for parallel multicore processing.
The four supported compilers are the open source ``gcc`` compiler, Microsoft Visual C ``msvc``, Intel's ``icc`` compiler, or the Apple's ``clang`` compiler.
The Intel compiler currently offers the best performance on x86 processors through the support of the AVX instruction set;
however, the ``gcc`` and ``clang`` compilers are often more readily available.

**Important:** You must first install one of these compilers together with the associated OpenMP libraries on your computer.
MacOS and Windows users should refer to the instructions :ref:`below <Windows and Mac>` for more details on installation of the compilers, OMP libraries and associated utilities.

Once the compiler and OMP libraries are installed, the following commands can be used to compile the ``svmbir`` code.

For installation using the four possible compiler options, run one of the following:

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

1. *Intel icc Compiler:*
The Intel compiler and OMP libraries when coupled with the appropriate Intel x86 processor
can substantially increase ``svmbir`` performance by enabling the AVX2 instructor set.
The ``icc/OpenMP`` compiler and libraries exists for Linux, Windows, and MacOS, but may need to be purchased.
The icc compiler is available `[here] <https://software.intel.com/content/www/us/en/develop/tools/parallel-studio-xe.html>`_.

2. *Windows Installation:* The package will run under Windows, but there tend to be more things that can go wrong due to the wide variety of possible configurations. The following list of recommended configurations have been tested to work, but others are possible:

* *64-bit gcc or Intel icc compiler:* For the command line version, make sure to install a 64bit compiler such as the ``MinGW_64`` available from `[here] <http://winlibs.com>`_ or the Intel ``icc`` compiler as described above. Commonly used gcc compilers are only 32bit and will create ``calloc`` errors when addressing array sizes greater than 2Gb.

* *MinGW + MSYS environment:* For the command line version, we recommend installing ``MinGW`` including the ``msys`` utilities. These utilities support a minimalist set of traditional UNIX tools.

* *Git Bash:* We recommend installing `[Git Bash] <https://gitforwindows.org>`_ to support bash scripting.

One known issue is that in some Windows bash environments the C executable ``mbir_ct.exe`` may not be properly moved to the ``bin`` directory.
If this occurs, then the problem can be resolved by manually moving the file.

3. *MacOS Installation:*
MacOS users will typically use the ``clang`` compiler provided as part of the Xcode Developer Tools.
In this case, the ``gcc`` command in the MacOS environment is **not** actually ``gcc``.
Instead it is an alias to the ``clang`` compiler.
Therefore, the C code should be compiled using the ``clang`` option.

In order to obtain ``clang`` you will need to install the most up-to-date version of both Xcode
and ``Command Line Tools for Xcode`` available `[here] <https://developer.apple.com/download/more/>`_.

Importantly, the Xcode Developer tools **do not include** the required OpenMP libraries.
The OMP libraries can be obtained from `[here] <https://mac.r-project.org/openmp/>`_.
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


4. *Compile C-Code (Legacy Instructions):*

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
