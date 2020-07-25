from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='svmbir',
   version='1.0',
   description="Python code for fast parallel-beam MBIR(Model Based Iterative Reconstruction) ",
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='Soumendu Majee',
   author_email='smajee@purdue.edu',
   packages=['svmbir'], 
   install_requires=['numpy', 'ruamel.yaml', 'matplotlib'], #external packages as dependencies
)

