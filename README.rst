svmbir
======

* Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)

* This is a python wrapper around HPImaging's supervoxel C code, [sv-mbir](https://github.com/HPImaging/sv-mbirct).

System Requirements
-------------------
1. GCC compiler version 4.8.5 or above
2. OpenMP API
3. Python>=3.6

(Python dependencies are automatically installed upon installation of svmbir)


Optional System Requirements for faster reconstruction
------------------------------------------------------
1. Intel-based CPU(s)
2. Intel ICC compiler (included in "Parallel Studio XE", available from Intel for Linux, macOS)

It is recommended that you install svmbir in a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Installation
------------
In command shell, ```cd``` to a directory of your choice and run the following commands to install from source.

1. Download Software
~~~~~~~~~~~~~~~~~~~~
Recursively clone the svmbir python code and the submodule with C code into a folder in the currect directory  

```git clone --recursive https://github.com/cabouman/svmbir.git```  

and change directory to the root directory of the repository.  

```cd svmbir```  

2. (Optional) Create Conda Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is recommended to use this code inside a conda environment.  

```conda env create -f environment.yml```  

This creates a conda environment with the required dependencies and  

```conda activate svmbir```  

activates the newly created conda environment. Before running the code, this conda environment should always be activated.

3. Compile Code
~~~~~~~~~~~~~~~
Option 1: Build the binary executable from the C source code using GCC. 

```make -C svmbir/sv-mbirct/src/ CC=gcc``` 

Option 2: If an Intel ICC compiler is present, then faster reconstruction can be achieved by building with ICC: 

```make -C svmbir/sv-mbirct/src/ CC=icc```  

Option 3: For MacOS, compile using the apple Clang compiler by running:  

```make -C svmbir/sv-mbirct/src/ CC=clang```  


4. Install the Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run the command  

```pip install .```  

which installs svmbir and its dependencies as a python package.

You can verify the installation by running ```pip show svmbir```, which should display a brief summary of the installed package.

After that, svmbir is installed in the system and can be used in any python script in any directory using the python command ```import svmbir```.


Demo
----
The script ```demo_simple.py``` contains a short demo that illustrates how to use the svmbir package for performing reconstructions.

To reconstruct your own data, use the interface used in ```demo_simple.py``` as a reference.

