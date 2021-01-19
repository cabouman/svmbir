**svmbir** stands for Super-Voxel Model-Based Iterative Reconstruction.
svmbir is an easy-to-use python package for fast parallel-beam reconstruction of tomography data using model-based priors.


Features
--------
* Easy-to-use python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)

* Interface to HPImaging's C code implementation of the super-voxel algorithm :cite:`wang2016high` :cite:`wang2017massively`, `[sv-mbirct] <https://github.com/HPImaging/sv-mbirct>`_

* Supports MBIR reconstruction with Bayesian and Plug-and-Play prior models.


System Requirements
-------------------
1. GCC compiler version 4.8.5 or above
2. OpenMP Libraries
3. Python>=3.6


Optional System Requirements
----------------------------
Fastest reconstruction can be obtained with,

* Intel-based CPU(s) supporting AVX2,AVX512
* Intel ICC compiler (in "Parallel Studio XE", and now free "oneAPI")

We also recommend:

* Installation using conda environment

License
-------
The project is licensed under the `BSD 3-Clause <https://github.com/cabouman/svmbir/blob/master/LICENSE>`_ License.


