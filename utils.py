# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

import os
import sys
import argparse
import random
import numpy as np
import pdb
from glob import glob
# pdb.set_trace()

import matplotlib.pyplot as plt
from PIL import Image
from ruamel.yaml import YAML

# ------- params read/modify ------------------

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


############################################################################
## mbir read/write Binary Files
############################################################################

def read_sino_openmbir(rootPath, suffix, N_theta, N_z, N_y):

    fname_list = generateFileList(N_z, rootPath, suffix)

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

    assert len(x.shape)==3, 'data must be 3D'

    x = np.copy(np.swapaxes(x, 0, 1), order='C') # shape = N_z x N_theta x N_y

    fname_list = generateFileList(x.shape[0], rootPath, suffix)

    for i, fname in enumerate(fname_list):

        with open(fname, 'wb') as fileID:
            x[i].astype('float32').flatten('C').tofile(fileID)

def read_recon_openmbir(rootPath, suffix, N_x, N_y, N_z):

    fname_list = generateFileList(N_z, rootPath, suffix)

    sizesArray = (N_z, N_y, N_x)
    x = np.zeros(sizesArray)

    for i, fname in enumerate(fname_list):

        with open(fname, 'rb') as fileID:
            numElements = sizesArray[1]*sizesArray[2]
            x[i] = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

    return x

def write_recon_openmbir(x, rootPath, suffix):

    assert len(x.shape)==3, 'data must be 3D'

    fname_list = generateFileList(x.shape[0], rootPath, suffix)

    for i, fname in enumerate(fname_list):

        with open(fname, 'wb') as fileID:
            x[i].astype('float32').flatten('C').tofile(fileID)

#############################################################################
## 3D read/write routines
#############################################################################

def read_recon3D(filePath):

    x = read_ND(filePath, 3, dtype='float32', ntype='int32') # shape = N_x x N_y x N_z
    x = np.copy(np.swapaxes(x, 0, 2), order='C')

    return x

def write_recon3D(x, filePath):

    assert len(x.shape)==3, 'data must be 3D'

    x = np.copy(np.swapaxes(x, 0, 2), order='C') # shape = N_x x N_y x N_z
    write_ND(x, filePath, dtype='float32', ntype='int32')


def read_sino3D(filePath):

    x = read_ND(filePath, 3, dtype='float32', ntype='int32') # shape = N_theta x N_y x N_z
    x = np.copy(np.swapaxes(x, 1, 2), order='C')

    return x

def write_sino3D(x, filePath):

    assert len(x.shape)==3, 'data must be 3D'

    x = np.copy(np.swapaxes(x, 1, 2), order='C') # shape = N_theta x N_y x N_z
    write_ND(x, filePath, dtype='float32', ntype='int32')


#############################################################################
## read/write N-D arrays as binary files
#############################################################################


def read_ND_list(fNameList, n_dim, dtype='float32', ntype='int32'):

    return [read_ND(fName, n_dim, dtype, ntype) for fName in fNameList ]


def write_ND_list(dataList, fNameList, order_type='recon'):

    assert len(fNameList)==len(dataList), 'write_ND_list: dimension mismatch'

    for data, fName in zip(dataList,fNameList):
        write_ND(data, fName, dtype, ntype)


def read_ND(filePath, n_dim, dtype='float32', ntype='int32'):

    with open(filePath, 'rb') as fileID:

        sizesArray = np.fromfile( fileID, dtype=ntype, count=n_dim)
        numElements = np.prod(sizesArray)
        dataArray = np.fromfile(fileID, dtype=dtype, count=numElements).reshape(sizesArray)

    return dataArray


def write_ND(dataArray, filePath, dtype='float32', ntype='int32'):

    sizesArray = np.asarray(dataArray.shape)

    with open(filePath, 'wb') as fileID:

        sizesArray.astype(ntype).flatten('C').tofile(fileID)
        dataArray.astype(dtype).flatten('C').tofile(fileID)


#############################################################################
## read/write Image Lists
#############################################################################

def read_stackOfFileNames(dirPathList, file_ext):

    # each directory must have stack of 3D-recon files (4D)
    stackOfFileNames = []
    for dirPath in dirPathList:

        wildCardFname = os.path.join(dirPath,'*.'+file_ext)
        fNameList = glob(wildCardFname)
        fNameList.sort()
        stackOfFileNames.append(fNameList)

    return stackOfFileNames

def generateFileList(numFiles, fileRoot, suffix):

    fileList = []
    for i in range(numFiles):
        fileList.append(fileRoot+str(i)+suffix)

    return fileList


def writeFileList(filePath, fileList):

    with open(filePath,'w') as fileID:
    
        fileID.write(str(len(fileList) )+"\n")
        for fileName in fileList:
            fileID.write(fileName+"\n")


def readFileList(filePath, resolvePath=True):

    with open(filePath,'r') as fileID:

        lines = fileID.read().split("\n")

    numLines = int(lines[0])
    fileList = lines[1:numLines+1]

    if resolvePath==True:
        origDir = os.path.dirname(filePath)
        for i in range(len(fileList)):
            tempPath = os.path.join(origDir, fileList[i])
            fileList[i] = os.path.abspath( tempPath )

    return fileList
