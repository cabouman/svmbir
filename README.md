# svmbir

*Python code for fast MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper for High Performance Imaging's supervoxel C code, [HPImaging/sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

Full documentation is available at: https://svmbir.readthedocs.io


## Installing svmbir

The svmbir package is available from conda-forge and PyPI.

- Create an empty virtural environment
```
conda create -n svmbir python=3.8
conda activate svmbir
```

- Install using conda

```
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install svmbir
```

- Install using pip (PyPI)

```
pip install svmbir
```

Note that pip installation requires a GNU gcc compiler.
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




