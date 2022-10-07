**svmbir** (super-voxel model-based iterative reconstruction) is an easy-to-use python package for fast iterative reconstruction of tomography data using model-based priors.
The `svmbir <https://github.com/cabouman/svmbir>`_ package is a python interface to HPImaging's optimized 
C implementation `[sv-mbirct] <https://github.com/HPImaging/sv-mbirct>`_
of the super-voxel algorithm :cite:`wang2016high` :cite:`wang2017massively`.


Features
--------
* Supports MBIR reconstruction with Bayesian and Plug-and-Play prior models
* Supports parallel-beam and fan-beam geometries


System Requirements
-------------------
* Python 3.8-3.10

Local builds also require,

* GCC compiler version 4.8.5 or above
* OpenMP Libraries


Optional System Requirements
----------------------------
Fastest reconstruction can be obtained with,

* Intel-based CPU(s) supporting AVX2,AVX512
* Intel ICC compiler (included with Intel's free "oneAPI" toolkit)

We also recommend installation to a conda virtual environment.


License
-------
The project is licensed under the `BSD 3-Clause <https://github.com/cabouman/svmbir/blob/master/LICENSE>`_ License.


