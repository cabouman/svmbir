import os
import numpy as np
from svmbir.cython.cysvmbir import *

# create output folder
os.makedirs('output', exist_ok=True)

# Set image parameters
py_imageparams = dict()
py_imageparams['Nx'] = 128
py_imageparams['Ny'] = 128
py_imageparams['Deltaxy'] = 1.0
py_imageparams['ROIRadius'] = np.float(py_imageparams['Deltaxy'] * max(py_imageparams['Ny'], py_imageparams['Nx']))/2.0
py_imageparams['DeltaZ'] = 1.0
py_imageparams['Nz'] = 80
py_imageparams['FirstSliceNumber'] = 0
py_imageparams['NumSliceDigits'] = 5

# Set sinogram parameters
py_sinoparams = dict()
py_sinoparams['NChannels'] = 128
py_sinoparams['DeltaChannel'] = 1.0
py_sinoparams['CenterOffset'] = 0.0
py_sinoparams['NViews'] = 32
py_sinoparams['ViewAngles'] = np.linspace(0,np.pi,py_sinoparams['NViews']).astype(np.single)
py_sinoparams['NSlices'] = 80
py_sinoparams['DeltaSlice'] = 1.0
py_sinoparams['FirstSliceNumber'] = 0
py_sinoparams['NumSliceDigits'] = 5

# Convert python string to bytearray. bytearray can be accepted by c function as char*.
temp_path = "./output/tmp"
len_path = len(temp_path)
Amatrix_fname = np.zeros(len_path+1).astype(np.ubyte)
Amatrix_fname[:len_path] = bytearray(temp_path.encode('ascii'))

# Compute A matrix
cy_AmatrixComputeToFile(py_imageparams, py_sinoparams, Amatrix_fname, 2)