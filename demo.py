
import os
from glob import glob
import numpy as np

from utils import *


fname = 'data/shepp_slice0001.2Dsinodata'
print(fname)

# y = read_sino_openmbir(fname, '.2Dsinodata', 288, 1, 512)

sizesArray = (1, 288, 512)
with open(fname, 'rb') as fileID:
    numElements = sizesArray[1]*sizesArray[2]
    x = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

print(x.shape)

np.save('data/sinodata.npy', x)

fname = 'data/shepp_slice0001.2Dweightdata'
print(fname)

# y = read_sino_openmbir(fname, '.2Dweightdata', 288, 1, 512)

sizesArray = (1, 288, 512)
with open(fname, 'rb') as fileID:
    numElements = sizesArray[1]*sizesArray[2]
    x = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

print(x.shape)

np.save('data/weightdata.npy', x)