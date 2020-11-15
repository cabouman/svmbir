============
Installation 
============

This section covers the basics of how to download and install svmbir.


Installing from PyPI or Conda
-----------------------------

At this time, the ``svmbir`` package must be built from source.
In the future, we also plan to make it installable from ``PyPI`` or ``Conda``.


Compiling the C code
--------------------

1. Download Software

In order to download the C code, ``cd`` to a directory of your choice and run the following commands to install from source.

``git clone --recursive https://github.com/cabouman/svmbir.git``

This command recursively downloads a folder containing the svmbir python wrapper along with the ``sv-mbirct`` C-code submodule.

Next, change your directory to the root directory of the repository using the command ``cd svmbir``.


2. Compile Code

Option 1: Build the binary executable from the C source code using GCC.

``make -C svmbir/sv-mbirct/src/ CC=gcc``

Option 2: If an Intel ICC compiler is present, then faster reconstruction can be achieved by building with ICC:

``make -C svmbir/sv-mbirct/src/ CC=icc``

Option 3: For MacOS, compile using the apple Clang compiler by running:

``make -C svmbir/sv-mbirct/src/ CC=clang``



Installing Python Package
-------------------------

1. (Optional) Create Conda Environment

It is recommended that you create a conda environment.
To do this, first install ``Anaconda``, and then create and activate an ``svmbir`` environment using the following two commands.

``conda env create -f environment.yml``

``conda activate svmbir``

This will create a conda environment with the required dependencies.
Before running the code, this ``svmbir`` conda environment should always be activated.


2. Install the Python Package

In order to install the ``svmbir`` package into your ``svmbir`` environment, first make sure the ``svmbir`` environment is active, and then run the following command

``pip install .``

You can verify the installation by running ``pip show svmbir``, which should display a brief summary of the packages installed in the ``svmbir`` environment.
Now you will be able to use the ``svmbir`` python commands from any directory by running the python command ``import svmbir``.


Updating svmbir
-----------------

Since the ``svmbir`` package is under active development, you may need to update your package in order to obtain the newest revisions. To do this, you will need to update both the C source code and executables along with the python package.

1. Updating the python installation

In order to update the python installation, activate the ``svmbir`` environment and run the following command.

``pip install . --upgrade``


2. Updating the C submodule

The C code generally changes less frequently, but to update it you should re-download the C source code. If you are using ``git``, then this may require the use of the command ``git submodule update``. Once the C source is updated, then recompile using the commands described above.

