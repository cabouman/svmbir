import os
from distutils.core import setup
from distutils.extension import Extension
from glob import glob

with open("README.md", "r") as fh:
    long_description = fh.read()

# sources = glob('svmbir/sv-mbirct/src/*.c')
# mbir_ct = Extension('svmbir/sv-mbirct/bin/mbir_ct',
#                     sources=sources,
#                     extra_compile_args=['-fopenmp', '-O3'], 
#                     extra_link_args=['-fopenmp'])

#assert os.path.exists('svmbir/sv-mbirct/bin/mbir_ct'), 'Compiled executable not present in svmbir/sv-mbirct/bin/. Compile the binary executable first'

if os.path.exists('svmbir/sv-mbirct/bin/mbir_ct'):
     exec_file='sv-mbirct/bin/mbir_ct'
elif os.path.exists('svmbir/sv-mbirct/bin/mbir_ct.exe'):
     exec_file='sv-mbirct/bin/mbir_ct.exe'
else:
     assert False, 'Compiled executable not present in svmbir/sv-mbirct/bin/. Compile the binary executable first'

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
     install_requires=['numpy', 'ruamel.yaml', 'matplotlib'], #external packages as dependencies
     package_data={'svmbir': [exec_file]}
     # package_data={'svmbir': ['sv-mbirct/bin/mbir_ct']}
     # ext_modules=[mbir_ct]
)

