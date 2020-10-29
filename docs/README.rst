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