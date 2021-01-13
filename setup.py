import os
import numpy as np
from setuptools import setup, Extension
from Cython.Distutils import build_ext

with open("README.md", "r") as fh:
    long_description = fh.read()

# Check for compiled executable
if os.path.exists('svmbir/sv-mbirct/bin/mbir_ct'):
     exec_file='sv-mbirct/bin/mbir_ct'
elif os.path.exists('svmbir/sv-mbirct/bin/mbir_ct.exe'):
     exec_file='sv-mbirct/bin/mbir_ct.exe'
else:
     assert False, 'Compiled executable not present in svmbir/sv-mbirct/bin/. Compile the binary executable first'

PACKAGES_DIR = 'svmbir'
PACKAGES = [PACKAGES_DIR]
SRC_DIR = PACKAGES_DIR + "/sv-mbirct/src/"

# OpenMP gcc compile: tested for MacOS and Linux
if os.environ.get('CC') =='gcc':
    c_extension = Extension(PACKAGES_DIR + ".cysvmbir",
                      [SRC_DIR + "A_comp.c", SRC_DIR + "allocate.c", SRC_DIR + "heap.c",
                       SRC_DIR + "icd3d.c", SRC_DIR + "initialize.c", SRC_DIR + "MBIRModularUtils.c",
                       SRC_DIR + "recon3d.c", PACKAGES_DIR + "/cysvmbir.pyx"],
                      libraries=[],
                      include_dirs=[np.get_include()],
                      # for gcc-10 "-std=c11" can be added as a flag
                      extra_compile_args=["-O3", "-fopenmp","-Wno-unknown-pragmas","-DTEST"],
                      extra_link_args=["-lm","-fopenmp","-DTEST"])

    # Install
    setup(
         name='svmbir',
         version='1.0',
         description="Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) ",
         long_description=long_description,
         long_description_content_type="text/markdown",
         author='Soumendu Majee',
         author_email='smajee@purdue.edu',
         packages=PACKAGES,
         python_requires='>=3.6',
         #external packages as dependencies
         install_requires=['numpy','ruamel.yaml','matplotlib','psutil','pytest','scikit-image','Cython'],
         package_data={'svmbir': [exec_file]},
         cmdclass = {"build_ext": build_ext},
         ext_modules = [c_extension]
    )
else:
    # Install
    setup(
        name='svmbir',
        version='1.0',
        description="Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) ",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Soumendu Majee',
        author_email='smajee@purdue.edu',
        packages=['svmbir'],
        python_requires='>=3.6',
        # external packages as dependencies
        install_requires=['numpy', 'ruamel.yaml', 'matplotlib', 'psutil', 'pytest', 'scikit-image'],
        package_data={'svmbir': [exec_file]}
    )

