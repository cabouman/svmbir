# svmbir


### Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) 
#### This is a python wrapper around the c super-voxel code: https://github.com/HPImaging/sv-mbirct

#### Optional System Requirements for faster reconstruction
1. Intel-based CPU(s)
2. Intel "icc" compiler (included in "Parallel Studio XE", available from Intel for Linux, macOS)

### Installation
##### Installation using gcc
Go to a directory of your choice and run the following commands to install from source.
These commands need to run EXACTLY.
```
git clone --recursive https://github.com/cabouman/svmbir.git
cd svmbir
make -C svmbir/sv-mbirct/src/ -f Makefile.gcc
pip install .
```
By running these commands, svmbir would be installed in the system and can be run from any directory.


##### Installation using icc (faster computation but requires Intel CPU(s) and Intel "icc" compiler)
Go to a directory of your choice and run the following commands to install from source.
These commands need to run EXACTLY.
```
git clone --recursive https://github.com/cabouman/svmbir.git
cd svmbir
make -C svmbir/sv-mbirct/src/
pip install .
```
By running these commands, svmbir would be installed in the system and can be run from any directory.

### Execution
```demo.py``` contains a short demo that demonstrates how to use the svmbir package for performing reconstructions.

