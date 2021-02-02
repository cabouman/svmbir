import os
import sys
import numpy as np
from setuptools import setup, Extension
from Cython.Distutils import build_ext

with open("README.md", "r") as fh:
    long_description = fh.read()

PACKAGES_DIR = 'svmbir'
PACKAGES = [PACKAGES_DIR]
SRC_DIR = PACKAGES_DIR + "/sv-mbirct/src/"

if os.environ.get('CLIB') !='CMD_LINE':
    #Check that compiler is set
    if os.environ.get('CC') not in ['gcc','icc','clang','msvc']:
        raise ValueError('CC flag not set to valid value. For example should be: CC=gcc')

    # OpenMP gcc compile: tested for MacOS and Linux
    if os.environ.get('CC') =='gcc':
        extra_compile_args=["-std=c11","-O3","-fopenmp","-Wno-unknown-pragmas"]
        extra_link_args=["-lm"]

    if os.environ.get('CC') =='icc':
        if sys.platform == 'linux':
            os.environ['LDSHARED'] = 'icc -shared'
        extra_compile_args=["-O3","-DICC","-qopenmp","-no-prec-div","-restrict","-ipo","-inline-calloc",
                            "-qopt-calloc","-no-ansi-alias","-xCORE-AVX2"]
        extra_link_args=["-lm"]

    if os.environ.get('CC') =='clang':
        extra_compile_args=["-O3","-Xclang", "-fopenmp","-Wno-unknown-pragmas"]
        extra_link_args=["-lm"]

    # build for Windows using MS Visual C++
    if os.environ.get('CC') =='msvc':
        extra_compile_args=["/std:c11","/O2","/openmp","/DMSVC"]
        extra_link_args=["-lm"]

    c_extension = Extension(PACKAGES_DIR + ".interface_cy_c",
                  [SRC_DIR + "A_comp.c", SRC_DIR + "allocate.c", SRC_DIR + "heap.c",
                   SRC_DIR + "icd3d.c", SRC_DIR + "initialize.c", SRC_DIR + "MBIRModularUtils.c",
                   SRC_DIR + "recon3d.c", PACKAGES_DIR + "/interface_cy_c.pyx"],
                  libraries=[],
                  include_dirs=[np.get_include()],
                  extra_compile_args=extra_compile_args,
                  extra_link_args=extra_link_args)

    # Install cython version
    setup(
         name='svmbir',
         version='1.0',
         description="Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) ",
         long_description=long_description,
         long_description_content_type="text/markdown",
         author='Soumendu Majee',
         author_email='smajee@purdue.edu',
         packages=PACKAGES,
         # python_requires='>=3.6',
         #external packages as dependencies
         install_requires=['numpy','ruamel.yaml','matplotlib','psutil','pytest','Pillow','Cython'],
         #package_data={'svmbir': [exec_file]},
         cmdclass = {"build_ext": build_ext},
         ext_modules = [c_extension]
    )
else:
    # Check for compiled executable
    if os.path.exists('svmbir/sv-mbirct/bin/mbir_ct') :
        exec_file = 'sv-mbirct/bin/mbir_ct'
    elif os.path.exists('svmbir/sv-mbirct/bin/mbir_ct.exe') :
        exec_file = 'sv-mbirct/bin/mbir_ct.exe'
    else :
        assert False, 'Compiled executable not present in svmbir/sv-mbirct/bin/. Compile the binary executable first'

    # Install command-line version
    setup(
        name='svmbir',
        version='1.0',
        description="Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) ",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Soumendu Majee',
        author_email='smajee@purdue.edu',
        packages=['svmbir'],
        # python_requires='>=3.6',
        # external packages as dependencies
        install_requires=['numpy', 'ruamel.yaml', 'matplotlib', 'psutil', 'pytest', 'Pillow'],
        package_data={'svmbir': [exec_file]}
    )


