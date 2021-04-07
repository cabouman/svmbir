# svmbir

*Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper around HPImaging's supervoxel C code, [sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

## Installation through testpypi
- Create an empty environment.
```
conda create -n svmbir python=3.8
```
- pip install from testpypi. 

For installation using the four possible compiler options(gcc, icc, clang, and msvc).
```
CC=gcc pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple svmbir
```

## Running the demos
1. Download demo.zip at https://github.com/cabouman/svmbir/blob/pypi/demo.zip.
2. Uncompress the zip file and change into demo folder.
3. In your terminal window, install required dependencies of demo. 
```
pip install -r requirements_demo.txt
```
4. In your terminal window, use python to run each demo.


Full documentation is available at: https://svmbir.readthedocs.io


