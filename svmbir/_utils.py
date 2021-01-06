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
    for key in common_keys :
        params[key] = kwargs[key]

    return params


def read_params(params_path):
    with open(params_path, 'r') as fileID :
        yaml = YAML()
        params = yaml.load(fileID)

    return params


def print_params(params, start_str = ''):
    for key, value in params.items() :
        if isinstance(value, dict) :
            print('{}:'.format(key))
            print_params(value, start_str='    ')
        else :
            print(start_str + '{}: {}'.format(key, value))


def modify_params(filePath, **kwargs):
    with open(filePath, 'r') as fileID :
        yaml = YAML()
        yaml_dict = yaml.load(fileID)

    # print(kwargs.keys())

    for key in kwargs.keys() :
        yaml_dict[key] = kwargs[key]

    with open(filePath, 'w') as fileID :
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

    with open(filePath, 'w') as fileID :
        yaml = YAML()
        yaml.dump(kwargs, fileID)


def readAngleList(filePath):
    with open(filePath, 'r') as fileID :
        lines = fileID.read().split("\n")

    angleList = []
    for line in lines :
        if not line.isspace() and line :
            angleList.append(float(line))

    return angleList


#########################################
## mbir read/write/delete Binary Files ##
#########################################

def read_sino_openmbir(rootPath, suffix, N_theta, N_z, N_y):
    fname_list = generateFileList(N_z, rootPath, suffix, numdigit=4)

    sizesArray = (N_z, N_theta, N_y)
    x = np.zeros(sizesArray, dtype=np.float32)

    for i, fname in enumerate(fname_list) :
        with open(fname, 'rb') as fileID :
            numElements = sizesArray[1] * sizesArray[2]
            x[i] = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

    # shape = N_z x N_theta x N_y
    x = np.copy(np.swapaxes(x, 0, 1), order='C')

    return x


def write_sino_openmbir(x, rootPath, suffix):
    # shape of x = N_theta x N_z  x N_y

    assert len(x.shape) == 3, 'data must be 3D'

    x = np.copy(np.swapaxes(x, 0, 1), order='C')

    fname_list = generateFileList(x.shape[0], rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list) :
        with open(fname, 'wb') as fileID :
            x[i].astype('float32').flatten('C').tofile(fileID)


def read_recon_openmbir(rootPath, suffix, N_x, N_y, N_z):
    fname_list = generateFileList(N_z, rootPath, suffix, numdigit=4)

    sizesArray = (N_z, N_y, N_x)
    x = np.zeros(sizesArray, dtype=np.float32)

    for i, fname in enumerate(fname_list) :
        with open(fname, 'rb') as fileID :
            numElements = sizesArray[1] * sizesArray[2]
            x[i] = np.fromfile(fileID, dtype='float32', count=numElements).reshape([sizesArray[1], sizesArray[2]])

    return x


def write_recon_openmbir(x, rootPath, suffix):
    # shape of x = N_z x N_y x N_x

    assert len(x.shape) == 3, 'data must be 3D'

    fname_list = generateFileList(x.shape[0], rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list) :
        with open(fname, 'wb') as fileID :
            x[i].astype('float32').flatten('C').tofile(fileID)


def generateFileList(numFiles, fileRoot, suffix, numdigit = 0):
    fileList = []
    for i in range(numFiles) :
        fileList.append(fileRoot + str(i).zfill(numdigit) + suffix)

    return fileList


def delete_data_openmbir(rootPath, suffix, num_files):
    fname_list = generateFileList(num_files, rootPath, suffix, numdigit=4)

    for i, fname in enumerate(fname_list) :
        os.remove(fname)


##############################
## Parameter Test Functions ##
##############################

def test_params_line0(sino, angles):

    # Test for valid sino structure, and if necessary, make it 3D
    assert isinstance(sino, np.ndarray) and ((sino.ndim == 3) or (sino.ndim == 2)), "Invalid sinogram input"
    if sino.ndim == 2 :
        sino = sino[:, np.newaxis, :]
        print("svmbir.recon() warning: Input sino array only 2D. Added singleton dimension to slice index to make it 3D.")

    assert isinstance(angles, np.ndarray) and (angles.ndim == 1), "Invalid angle array input"

    return sino


def test_params_line1(center_offset, delta_channel, delta_pixel):

    if not isinstance(center_offset, float):
        warnings.warn("Parameter center_offset is not valid float; Setting center_offset = 0.0.")
        center_offset = 0.0

    if not isinstance(delta_channel, float):
        warnings.warn("Parameter delta_channel is not valid float; Setting delta_channel = 1.0.")
        delta_channel = 1.0

    if not ((delta_pixel is None) or (isinstance(delta_pixel, float) and (delta_pixel > 0))):
        warnings.warn("Parameter delta_pixel is not valid float; Setting delta_pixel = 1.0.")
        delta_pixel = 1.0

    return center_offset, delta_channel, delta_pixel


def test_params_line2(num_rows, num_cols, roi_radius):

    if not ((roi_radius is None) or isinstance(num_rows, int)):
        warnings.warn("Parameter num_rows is not valid int; Setting num_rows = None.")
        num_rows = None

    if not ((roi_radius is None) or isinstance(num_cols, int)):
        warnings.warn("Parameter num_rows is not valid int; Setting num_cols = None.")
        num_cols = None

    if not ((roi_radius is None) or ((isinstance(roi_radius, float) and (roi_radius > 0)))):
        warnings.warn("Parameter roi_radius is not valid float; Setting roi_radius = None.")
        roi_radius = None

    return num_rows, num_cols, roi_radius


def test_params_line3(sigma_y, snr_db, weights, weight_type):

    if not ((sigma_y is None) or (isinstance(sigma_y, float) and (sigma_y > 0))):
        warnings.warn("Parameter sigma_y is not valid float; Setting sigma_y = None.")
        sigma_y = None

    if not isinstance(snr_db, float):
        warnings.warn("Parameter snr_db is not valid float; Setting snr_db = 30.")
        snr_db = 30

    if not ((weights is None) or (isinstance(weights, np.ndarray) or (weights.ndim == 3))):
        warnings.warn("Parameter weights is not valid 3D np array; Setting weights = None.")
        weights = None

    list_of_weights = ['unweighted', 'transmission', 'transmission_root', 'emission']
    if not (isinstance(weight_type, str) and (weight_type in list_of_weights)):
        warnings.warn("Parameter weight_type is not valid string; Setting roi_radius = 'unweighted'")
        weight_type = 'unweighted'

    return sigma_y, snr_db, weights, weight_type


def test_params_line4(sharpness, positivity, sigma_x):

    if not isinstance(sharpness, float):
        warnings.warn("Parameter sharpness is not valid float; Setting sharpness = 0.0.")
        sharpness = 0.0

    if not isinstance(positivity, bool):
        warnings.warn("Parameter positivity is not valid boolean; Setting positivity = True.")
        positivity = True

    if not ((sigma_x is None) or isinstance(sigma_x, float)):
        warnings.warn("Parameter weights is not valid float; Setting weights = None.")
        weights = None

    return sharpness, positivity, sigma_x


def test_pqtb_values(p, q, T, b_interslice):
    """ Tests that p, q have valid values; prints warnings if necessary; and returns valid values.
    """

    # Check that p, q, T, b_interslice are floats
    if not isinstance(q, float):
        q = 2.0
        warnings.warn("Parameter q is wrong type; Setting q = 2.0")

    if not isinstance(p, float):
        p = 1.2
        warnings.warn("Parameter q is wrong type; Setting q = 2.0")

    if not isinstance(T, float):
        T = 1.0
        warnings.warn("Parameter T is wrong type; Setting T = 1.0")

    if not isinstance(b_interslice, float):
        b_interslice = 1.0
        warnings.warn("Parameter T is wrong type; Setting b_interslice = 1.0")

    # Check that q is valid
    if not (1.0 <= q <= 2.0):
        q = 2.0
        warnings.warn("Parameter q not in the valid range of [1,2]; Setting q = 2.0")

    # Check that p is valid
    if not (p >= 1.0):
        p = 1.0
        warnings.warn("Parameter p < 1; Setting p = 1.0")

    if not (p <= 2.0):
        p = 2.0
        warnings.warn("Parameter p > 2; Setting p = 2.0")

    # Check that p and q are jointly valid
    if not (p < q):
        p = q
        warnings.warn("Parameter p > q; Setting p = q.0")

    return p, q, T, b_interslice


def test_params_line5(init_image, prox_image, init_proj):

    if not (isinstance(init_image, float) or (isinstance(init_image, np.ndarray) and (init_image.ndim == 3))):
        warnings.warn("Parameter init_image is not either a valid float or 3D np array; Setting init_image = 0.0.")
        init_image = 0.0

    if not ((prox_image is None) or (isinstance(prox_image, np.ndarray) and (prox_image.ndim == 3))):
        warnings.warn("Parameter prox_image is not a valid 3D np array; Setting prox_image = None.")
        prox_image = None

    if not ((init_proj is None) or (isinstance(init_proj, np.ndarray) and (init_proj.ndim == 3))):
        warnings.warn("Parameter init_proj is not a valid 3D np array; Setting init_proj = None.")
        init_proj = None

    return init_image, prox_image, init_proj


def test_params_line6(max_resolutions, stop_threshold, max_iterations):

    if not (isinstance(max_resolutions, int) and (max_resolutions >= 0)):
        warnings.warn("Parameter max_resolutions is not valid int; Setting max_resolutions = 0.")
        max_resolutions = 0

    if not (isinstance(stop_threshold, float) and (stop_threshold >= 0)):
        warnings.warn("Parameter stop_threshold is not valid float; Setting stop_threshold = 0.0.")
        stop_threshold = 0.0

    if not (isinstance(max_iterations, int) and (max_iterations > 0)):
        warnings.warn("Parameter max_iterations is not valid int; Setting max_iterations = 100.")
        max_iterations = 100

    return max_resolutions, stop_threshold, max_iterations


def test_params_line7(num_threads, delete_temps, verbose):

    if not (isinstance(num_threads, int) and (num_threads > 0)):
        warnings.warn("Parameter num_threads is not valid int; Setting num_threads = None.")
        num_threads = None

    if not isinstance(delete_temps, bool):
        warnings.warn("Parameter delete_temps is not valid boolean; Setting delete_temps = True.")
        delete_temps = True

    if not (isinstance(verbose, int) and (verbose >= 0)):
        warnings.warn("Parameter verbose is not valid int; Setting verbose = 100.")
        verbose = 1

    return num_threads, delete_temps, verbose
