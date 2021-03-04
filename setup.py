import os
import re
import sys
import numpy as np
import warnings
from setuptools import setup, Extension
from Cython.Distutils import build_ext

with open("README.md", "r") as fh:
    long_description = fh.read()

name = 'svmbir'
version = '1.2.6.2'
description="Python code for fast parallel-beam MBIR (Model Based Iterative Reconstruction) "
long_description_content_type="text/markdown"
author = 'Soumendu Majee'
author_email = 'smajee@purdue.edu'

packages_dir = 'svmbir'
packages = [packages_dir]
src_dir = packages_dir + "/sv-mbirct/src/"

# Check for compiled executable
if os.path.exists('svmbir/sv-mbirct/bin/mbir_ct'):
    exec_file = 'sv-mbirct/bin/mbir_ct'
elif os.path.exists('svmbir/sv-mbirct/bin/mbir_ct.exe'):
    exec_file = 'sv-mbirct/bin/mbir_ct.exe'
else:
    exec_file = None

# If binary is present, include with installation
if exec_file is None:
    package_data={}
else:
    package_data={'svmbir': [exec_file]}

# First block is cython installation
if os.environ.get('CLIB') !='CMD_LINE':

    #Check that compiler is set
    if os.environ.get('CC') not in ['gcc','icc','clang','msvc'] and re.findall('gcc',str(os.environ.get('CC')))==[]:
        warnings.warn('CC environment variable not set to valid value. Using default CC=gcc.')
        os.environ["CC"] = 'gcc'
        #raise ValueError('CC flag not set to valid value. For example should be: CC=gcc')

    # OpenMP gcc compile: tested for MacOS and Linux
    if os.environ.get('CC') =='gcc' or re.findall('gcc',str(os.environ.get('CC')))!=[]:
        extra_compile_args=["-std=c11","-O3","-fopenmp","-Wno-unknown-pragmas"]
        extra_link_args=["-lm","-fopenmp"]

    if os.environ.get('CC') =='icc':
        if sys.platform == 'linux':
            os.environ['LDSHARED'] = 'icc -shared'
        extra_compile_args=["-O3","-DICC","-qopenmp","-no-prec-div","-restrict","-ipo","-inline-calloc",
                            "-qopt-calloc","-no-ansi-alias","-xCORE-AVX2"]
        extra_link_args=["-lm","-qopenmp"]

    if os.environ.get('CC') =='clang':
        extra_compile_args=["-O3","-Xclang", "-fopenmp","-Wno-unknown-pragmas"]
        extra_link_args=["-lm","-lomp"]

    # build for Windows using MS Visual C++
    if os.environ.get('CC') =='msvc':
        extra_compile_args=["/std:c11","/O2","/openmp","/DMSVC"]
        extra_link_args=["-lm"]

    c_extension = Extension(packages_dir + ".interface_cy_c",
                            [src_dir + "A_comp.c", src_dir + "allocate.c", src_dir + "heap.c",
                             src_dir + "icd3d.c", src_dir + "initialize.c", src_dir + "MBIRModularUtils.c",
                             src_dir + "recon3d.c", packages_dir + "/interface_cy_c.pyx"],
                            libraries=[],
                            include_dirs=[np.get_include()],
                            extra_compile_args=extra_compile_args,
                            extra_link_args=extra_link_args)

    # Install cython version
    setup(
         name=name,
         version=version,
         description=description,
         long_description=long_description,
         long_description_content_type=long_description_content_type,
         author=author,
         author_email=author_email,
         packages=packages,
         #external packages as dependencies
         install_requires=['numpy', 'Cython', 'psutil', 'Pillow'],
         package_data=package_data,
         cmdclass = {"build_ext": build_ext},
         ext_modules = [c_extension]
    )
else:

    # Check for compiled executable
    if exec_file is None:
        assert False, 'Compiled executable not present in svmbir/sv-mbirct/bin/. Compile the binary executable first'

    # Install command-line version
    setup(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        long_description_content_type=long_description_content_type,
        author=author,
        author_email=author_email,
        packages=packages,
        # external packages as dependencies
        install_requires=['numpy', 'ruamel.yaml', 'psutil', 'Pillow'],
        package_data=package_data
    )

