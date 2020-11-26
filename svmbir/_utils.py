
import os
import sys
from glob import glob
import numpy as np
import pdb
import warnings
# pdb.set_trace()

from ruamel.yaml import YAML

##################################
## mbir read/modify Param Files ##
##################################

def parse_params(default_params, **kwargs):
    
    params = dict(default_params)
    common_keys = set(kwargs.keys()) & set(params.keys())
    for key in common_keys:
        params[key] = kwargs[key]
    
    return params


def read_params(params_path):

    with open(params_path, 'r') as fileID:
        yaml = YAML()
        params = yaml.load(fileID)
        
    return params


def print_params(params, start_str=''):

    for key,value in params.items():
        if isinstance(value, dict):
            print('{}:'.format(key))
            print_params(value, start_str='    ')
        else:
            print(start_str+'{}: {}'.format(key,value))


def modify_params(filePath, **kwargs):
    
    with open(filePath, 'r') as fileID:
        yaml = YAML()
        yaml_dict = yaml.load(fileID)

    # print(kwargs.keys())

    for key in kwargs.keys():
        yaml_dict[key] = kwargs[key]

    with open(filePath, 'w') as fileID:
        yaml.dump(yaml_dict, fileID)


def sanitize_params(params):

    if isinstance(params, dict):
        params = dict(params)
        for key in params:
            params[key] = sanitize_params(params[key])

    if isinstance(params, (np.ndarray, np.generic)):
        params = params.tolist()

    return params


def write_params(filePath, **kwargs):

    kwargs = sanitize_params(kwargs)
    # print(kwargs)
    # sys.stdout.flush()

    with open(filePath, 'w') as fileID:
        yaml = YAML()
        yaml.dump(kwargs, fileID)


def readAngleList(filePath):

    with open(filePath,'r') as fileID:
        lines = fileID.read().split("\n")

    angleList = []
    for line in lines:
        if not line.isspace() and line:
            angleList.append(float(line))

    return angleList


#########################################
## mbir read/write/delete Binary Files ##
#########################################

def read_sino_openmbir(rootPath, suffix, N_theta, N_z, N_y):

    fname_list = generateFileList(N_z, rootPath, suffix, numdigit=4)

    sizesArray = (N_z, N_theta, N_y)
    x = np.zeros(sizesArray,dtype=np.float32)

    for i, fname in enumerate(fname_list):

        with open(fname, 'rb') as fileID:
            numElements = sizesArray[1]*sizesArray[2]
            x[i] = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

    # shape = N_z x N_theta x N_y
    x = np.copy(np.swapaxes(x, 0, 1), order='C')

    return x


def write_sino_openmbir(x, rootPath, suffix):

    # shape of x = N_theta x N_z  x N_y

    assert len(x.shape)==3, 'data must be 3D'

    x = np.copy(np.swapaxes(x, 0, 1), order='C') 

    fname_list = generateFileList(x.shape[0], rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list):

        with open(fname, 'wb') as fileID:
            x[i].astype('float32').flatten('C').tofile(fileID)


def read_recon_openmbir(rootPath, suffix, N_x, N_y, N_z):

    fname_list = generateFileList(N_z, rootPath, suffix, numdigit=4)

    sizesArray = (N_z, N_y, N_x)
    x = np.zeros(sizesArray,dtype=np.float32)

    for i, fname in enumerate(fname_list):

        with open(fname, 'rb') as fileID:
            numElements = sizesArray[1]*sizesArray[2]
            x[i] = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

    return x


def write_recon_openmbir(x, rootPath, suffix):

    # shape of x = N_z x N_y x N_x

    assert len(x.shape)==3, 'data must be 3D'

    fname_list = generateFileList(x.shape[0], rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list):

        with open(fname, 'wb') as fileID:
            x[i].astype('float32').flatten('C').tofile(fileID)


def generateFileList(numFiles, fileRoot, suffix, numdigit=0):

    fileList = []
    for i in range(numFiles):
        fileList.append(fileRoot+str(i).zfill(numdigit)+suffix)

    return fileList


def delete_data_openmbir(rootPath, suffix, num_files):

    fname_list = generateFileList(num_files, rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list):
        os.remove(fname)

##########################################
## mbir Test for valid parameter values ##
##########################################

def test_pq_values(p,q):
    """ Tests that p, q have valid values; prints warnings if necessary; and returns valid values.
    """

    if q < 1 or q > 2:
        warnings.warn("Parameter q not in the valid range of [1,2]; Setting q = 2.")
        q = 2

    if p < 1:
        warnings.warn("Parameter p < 1; Setting p = 1.")
        p = 1

    if p > 2:
        warnings.warn("Parameter p > 2; Setting p = 2.")
        p = 2

    if p > q:
        warnings.warn("Parameter p > q; Setting p = q.")
        p = q

    return p, q


def test_parameter_values(delta_channel, delta_pixel, roi_radius) :
    """ Tests that delta_channel, delta_pixel, roi_radius have valid values; prints warnings if necessary; and returns valid values.
    """

    if not ( isinstance(delta_channel,float) and (delta_channel > 0) ) :
        warnings.warn("Parameter delta_channel is not valid float; Setting delta_channel = 1.0.")
        delta_channel = 1.0

    if not ( isinstance(delta_pixel,float) and (delta_pixel > 0) ) :
        warnings.warn("Parameter delta_pixel is not valid float; Setting delta_pixel = 1.0.")
        delta_pixel = 1.0

    if not ( isinstance(roi_radius,float) and (roi_radius > 0) ) :
        warnings.warn("Parameter roi_radius is not valid float; Setting roi_radius = 1.0.")
        roi_radius = 1.0

    return delta_channel, delta_pixel, roi_radius
