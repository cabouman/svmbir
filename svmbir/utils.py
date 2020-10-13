
import os
import sys
from glob import glob
import numpy as np
import pdb
# pdb.set_trace()

from ruamel.yaml import YAML

############################################################################
## mbir read/modify Param Files
############################################################################

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
    print(kwargs)

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


############################################################################
## mbir read/write/delete Binary Files
############################################################################

def read_sino_openmbir(rootPath, suffix, N_theta, N_z, N_y):

    fname_list = generateFileList(N_z, rootPath, suffix, numdigit=4)

    sizesArray = (N_z, N_theta, N_y)
    x = np.zeros(sizesArray) 

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
    x = np.zeros(sizesArray)

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



