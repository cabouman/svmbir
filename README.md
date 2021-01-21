# svmbir

*Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper around HPImaging's supervoxel C code, [sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

Full documentation is available at: https://svmbir.readthedocs.io

## Guidelines for Contributing
Fork from the master branch, and ask for pull request to contribute.
Before asking for a pull request, please run all unit tests by running

 1.  ```CC=gcc python setup.py build_ext --inplace```
  
 2. ```pytest```
  
  Compilers other than gcc can also be used.
