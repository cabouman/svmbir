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

Full documentation is available at: https://svmbir.readthedocs.io


