
import os
from glob import glob
import numpy as np

from utils import *


fname = '../data/'

y = read_sino_openmbir(fname, '.2Dsinodata', 288, 1, 512):