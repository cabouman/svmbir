# svmbir

*Python code for fast MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper for the supervoxel C code [sv-mbirct](https://github.com/HPImaging/sv-mbirct) written by High Performance Imaging, a copy of which is in this repository.*

Full documentation is available at [svmbir_docs](https://svmbir.readthedocs.io).

To cite this software package, please use the bibtext entry at [cite_svmbir](https://svmbir.readthedocs.io/en/latest/credits.html#references).

## Installing svmbir

Currently supporting Python 3.10 or later, on MacOS and Linux (Windows possible but not actively maintained).

**svmbir** packages are available from conda-forge and PyPI, or can be built and installed from source.

- (recommended) Create a clean virtural environment, such as

```
conda create -n svmbir python=3.10
conda activate svmbir
```

- To install from conda-forge,

```
conda install -c conda-forge svmbir
```

- To install from PyPI,

```
pip install svmbir
```

- Installing from source (Linux: gcc; MacOS: clang plus `conda install -c conda-forge llvm-openmp`; see the [install page](https://svmbir.readthedocs.io/en/latest/install.html)),

```
# In top repository folder,
pip install .
```

See [here](https://svmbir.readthedocs.io/en/latest/install.html#)
for more details.



## Running the demos
1. Clone the repository (see above) and change into its `demo` folder.
2. In your terminal window, install the demo dependencies.
```
pip install "svmbir[demo]"
```
3. In your terminal window, use python to run each demo.




