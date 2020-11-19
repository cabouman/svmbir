============
Installation 
============

This section covers the basics of how to download and install svmbir.
At this time, the ``svmbir`` package must be built from source.
In the future, we also plan to make it installable from ``PyPI`` or ``Conda``.


Downloading and Compiling C code
--------------------------------

1. *Download C-code:*
In order to download the C code, move to a directory of your choice and run the following two commands.

``git clone --recursive https://github.com/cabouman/svmbir.git``

``cd svmbir``

This first command recursively downloads a folder containing the svmbir python wrapper along with the ``sv-mbirct`` C-code submodule,
and the second command moves into the root directory of the repository.
*Warning: Do not* used standard GUI methods to clone the repository because they may not recursively copy the C-code submodule. 


2. *Compile C-Code:*

The ``svmbir`` package requires a C compiler together with the OpenMP libraries for parallel multicore processing.
The three supported compilers are the open source ``gcc`` compiler, Intel's ``icc`` compiler, or the Apple's ``clang`` compiler.
The Intel compiler currently offers the best performance on x86 processors through the support of the AVX instruction set;
however, the ``gcc`` and ``clang`` compilers are often more readily available.

The section below provides details on installation of the selected compiler and associated OMP libraries.
Once the compiler and OMP libraries are installed, the following commands can be used to compile the ``svmbir`` code.

For ``gcc`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=gcc``

For ``icc`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=icc``

For ``clang`` compilation, run:

``make -C svmbir/sv-mbirct/src/ CC=clang``

In each case, the commands should be run from the root directory of the repository.
Also, see the sections below for trouble shooting tips for installing under the different operating systems.


Installing Python Package
-------------------------

1. *(Optional) Create Conda Environment:*
It is recommended that you create a conda environment.
To do this, first install ``Anaconda``, and then create and activate an ``svmbir`` environment using the following two commands.

``conda env create -f environment.yml``

``conda activate svmbir``

This will create a conda environment with the required dependencies.
Before running the code, this ``svmbir`` conda environment should always be activated.


2. *Install the Python Package:*
In order to install the ``svmbir`` package into your ``svmbir`` environment, first make sure the ``svmbir`` environment is active, and then run the following command

``pip install .``

You can verify the installation by running ``pip show svmbir``, which should display a brief summary of the packages installed in the ``svmbir`` environment.
Now you will be able to use the ``svmbir`` python commands from any directory by running the python command ``import svmbir``.


Updating svmbir
-----------------

Since the ``svmbir`` package is under active development, you may need to update your package in order to obtain the newest revisions. To do this, you will need to update both the C source code and executables along with the python package.

1. *Updating the python installation:*
In order to update the python installation, activate the ``svmbir`` environment and run the following command.

``pip install . --upgrade``


2. *Updating the C submodule:*
The C code generally changes less frequently, but to update it you must re-download the C source code. 
The easiest and safest way to update the C-code is to delete the entire ``svmbir`` repository and reclone it using the recursive clone command. 
However, you can also update it by updating the submodule pointer and running the command ``git submodule update``. 
Once the C source is updated, then recompile using the commands described above.


Installation of Compiler and Software on Windows and MacOS
----------------------------------------------------------

Below are some tips for compiling and running the package under the Windows and MacOSx operating systems.
Linux is more straight forward.

1. *Intel icc Compiler:*
The Intel compiler and OMP libraries when coupled with the appropriate Intel x86 processor
can substantially increase ``svmbir`` performance by enabling the AVX2 instructor set.
The ``icc/OpenMP`` compiler and libraries exists for Linux, Windows, and MacOS, but may need to be purchased.
The icc compiler is available `[here](https://software.intel.com/content/www/us/en/develop/tools/parallel-studio-xe.html)`_.

`[sv-mbir] <https://github.com/HPImaging/sv-mbirct>`_

2. *Windows Installation:* The package will run under Windows, but there tend to be more things that can go wrong due to the wide variety of possible configurations. The following list of recommended configurations have been tested to work, but others are possible:

* *64-bit gcc or Intel icc compiler:* Make sure to install a 64bit compiler such as the ``MinGW_64`` available from [here](http://winlibs.com) or the Intel ``icc`` compiler as described above. Commonly used gcc compilers are only 32bit and will create ``calloc`` errors when addressing array sizes greater than 2Gb.

* *MinGW + MSYS environment:* We recommend installing ``MinGW`` including the ``msys`` utilities. These utilities support a minimalist set of traditional UNIX tools.

* *Git Bash:* We recommend installing `[Git Bash](https://gitforwindows.org)`_ to support bash scripting.

One known issue is that in some Windows bash environments the C executable ``mbir_ct.exe`` may not be properly moved to the ``bin`` directory.
If this occurs, then the problem can be resolved by manually moving the file.

3. *MacOS Installation:*
MacOS users will typically use the ``clang`` compiler provided as part of the Xcode Developer Tools.
In this case, the ``gcc`` command in the MocOS environment is **not** actually gcc.
Instead it is an alias to the ``clang`` compiler.
Therefore, the C code should be compiled using the ``clang`` option.

In order to obtain ``clang`` you will need to install the most up-to-date version of both Xcode
and ``Command Line Tools for Xcode`` available `[here](https://developer.apple.com/download/more/)`_.

Importantly, the Xcode Developer tools **do not include** the required OpenMP libraries.
The OMP libraries can be obtained from `[here](https://mac.r-project.org/openmp/)`_.

In addition, after OS updates, you may need to reinstall the Xcode toolkit using the command: ``xcode-select --install``
