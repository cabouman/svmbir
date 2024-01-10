# svmbir

*Python code for fast MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper for High Performance Imaging's supervoxel C code, [HPImaging/sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

Full documentation is available at [svmbir_docs](https://svmbir.readthedocs.io).

To cite this software package, please use the bibtext entry at [cite_svmbir](https://svmbir.readthedocs.io/en/latest/credits.html#references).

## Installing svmbir

Currently supporting Python 3.9-3.12, on MacOS and Linux (Windows possible but not actively maintained).

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

- Installing from source (requires GNU/gcc compiler, OMP libraries),

```
# In top repository folder,
CC=gcc pip install .        # also supports Intel "icc"
```

See [here](https://svmbir.readthedocs.io/en/latest/install.html#)
for more details.



## Running the demos
1. Download demo.zip at https://github.com/cabouman/svmbir/blob/master/demo.zip.
2. Uncompress the zip file and change into demo folder.
3. In your terminal window, install required dependencies of demo. 
```
pip install -r requirements_demo.txt
```
4. In your terminal window, use python to run each demo.




