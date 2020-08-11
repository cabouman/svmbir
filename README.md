# svmbir


### Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) 
#### This is a python wrapper around the c super-voxel code: https://github.com/HPImaging/sv-mbirct

#### Optional System Requirements for faster reconstruction
1. Intel-based CPU(s)
2. Intel "icc" compiler (included in "Parallel Studio XE", available from Intel for Linux, macOS)

### Installation
Go to a directory of your choice and run the following commands to install from source.
These commands need to run EXACTLY.
##### 1. ```git clone --recursive https://github.com/cabouman/svmbir.git```

This clones the svmbir python code and the submodule written in c into a folder in the currect directory.

#### 2. ```cd svmbir```

This changes into the root directory of the repository.

##### 3. ```make -C svmbir/sv-mbirct/src/ -f Makefile.gcc```

This builds the binary executable from the C source code using GCC.
If Intel ICC compiler is present, then faster reconstruction can be achieved by building with ICC:
```make -C svmbir/sv-mbirct/src/```

##### 4. ```pip install .```

This installs svmbir and its dependencies as a python package.
To make sure that svmbir has been installed run ```pip list``` to see the list of installed python packages.

After svmbir is installed in the system and can be used in any python script in any directory using the command ```import svmbir```


### Execution
```demo.py``` contains a short demo that demonstrates how to use the svmbir package for performing reconstructions.

The file ```demo.py``` and the ```data``` directory can be copied together to any directory and it should still run if the installation is successful.

