# svmbir

*Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction)  
This is a python wrapper around HPImaging's supervoxel C code, [sv-mbirct](https://github.com/HPImaging/sv-mbirct).*

Full documentation is available at: https://svmbir.readthedocs.io


## Installation through pypi
- Create an empty environment.
```
conda create -n svmbir python=3.8
```
- pip install from pypi. 


If you have the standard gcc compiler (note that the compiler shipped with Mac OS is not the standard gcc - 
see the [documentation for detailed installation instructions for Mac](https://svmbir.readthedocs.io/en/latest/install.html#installation-on-windows-and-macos]))
then you can install using
```
pip install svmbir
```

For installation with other compilers, see the [installation instructions](https://svmbir.readthedocs.io/en/latest/install.html#).
## Running the demos
1. Download demo.zip at https://github.com/cabouman/svmbir/blob/master/demo.zip.
2. Uncompress the zip file and change into demo folder.
3. In your terminal window, install required dependencies of demo. 
```
pip install -r requirements_demo.txt
```
4. In your terminal window, use python to run each demo.




