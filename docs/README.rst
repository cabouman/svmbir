**svmbir** stands for Super-Voxel Model-Based Iterative Reconstruction.
svmbir is an easy-to-use python package for fast parallel-beam reconstruction of tomography data using model-based priors.


Features
--------
* Easy-to-use python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)

* Based on HPImaging's C code implementation of the super-voxel algorithm :cite:`wang2016high` :cite:`wang2017massively`,
[sv-mbir](https://github.com/HPImaging/sv-mbirct).

* Supports MBIR reconstruction with Bayesian and Plug-and-Play prior models.


System Requirements
-------------------
1. GCC compiler version 4.8.5 or above
2. OpenMP API
3. Python>=3.6


Optional System Requirements
----------------------------
For faster reconstruction using Intel's AVX2 instruction set, we recommend:

* Intel-based CPU(s)
* Intel ICC compiler (included in "Parallel Studio XE", available from Intel for Linux, macOS)

We also recommend:

* Installation using conda environment

License
-------
The project is licensed under the BSD 3-Clause License.

