# svmbir

*Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper around HPImaging's supervoxel C code, [sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

Full documentation is available at: https://svmbir.readthedocs.io


## Installation through pypi
- Create an empty virtural environment
```
conda create -n svmbir python=3.8
conda activate svmbir
```

- Install using pip (PyPI)

```
pip install svmbir
```

Note that installation requires a GNU gcc compiler.
See [here](https://svmbir.readthedocs.io/en/latest/install.html#)
for more details.

- Install using conda

The svmbir package is also available from the conda-forge channel.

```
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install svmbir
```

Note that installation requires a GNU gcc compiler.
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




