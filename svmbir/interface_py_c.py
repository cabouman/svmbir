# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 by SVMBIR Developers
# All rights reserved. BSD 3-clause License.

# These imports are needed only for read/write and command line interfaces
import subprocess
import os
import numpy as np
import svmbir._utils as utils
from ruamel.yaml import YAML

"""
Overview:
"""

##################################################################
# Items that are needed for read/write to disk interface
##################################################################
__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__), 'sv-mbirct', 'bin', 'mbir_ct'))

__namelen_sysmatrix = 20

_map_pyconv2camelcase = {'prior_model' : 'PriorModel',
                         'init_image_value' : 'InitImageValue',
                         'p' : 'p',
                         'q' : 'q',
                         'T' : 'T',
                         'sigma_x' : 'SigmaX',
                         'sigma_y' : 'SigmaY',
                         'b_nearest' : 'b_nearest',
                         'b_diag' : 'b_diag',
                         'b_interslice' : 'b_interslice',
                         'stop_threshold' : 'StopThreshold',
                         'max_iterations' : 'MaxIterations',
                         'positivity' : 'Positivity',
                         'relax_factor' : 'RelaxFactor',
                         'weight_type' : 'weightType',
                         'geometry' : 'Geometry',
                         'dist_source_detector' : 'DistSourceDetector',
                         'magnification' : 'Magnification',
                         'num_channels' : 'NChannels',
                         'num_views' : 'NViews',
                         'num_slices' : 'NSlices',
                         'delta_channel' : 'DeltaChannel',
                         'center_offset' : 'CenterOffset',
                         'delta_slice' : 'DeltaSlice',
                         'first_slice_number' : 'FirstSliceNumber',
                         'view_angle_list' : 'ViewAngleList',
                         'delta_xy' : 'Deltaxy',
                         'delta_z' : 'DeltaZ',
                         'roi_radius' : 'ROIRadius'}



def _gen_paths(svmbir_lib_path = __svmbir_lib_path, object_name = 'object', sysmatrix_name = 'object'):
    os.makedirs(os.path.join(svmbir_lib_path, 'obj'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'sino'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'weight'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'recon'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'init'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'proj'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'init_proj'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'prox'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'sysmatrix'), exist_ok=True)
    os.makedirs(os.path.join(svmbir_lib_path, 'par'), exist_ok=True)

    paths = dict()
    paths['sino_name'] = os.path.join(svmbir_lib_path, 'sino', object_name)
    paths['wght_name'] = os.path.join(svmbir_lib_path, 'weight', object_name)
    paths['recon_name'] = os.path.join(svmbir_lib_path, 'recon', object_name)
    paths['init_name'] = os.path.join(svmbir_lib_path, 'init', object_name)
    paths['proj_name'] = os.path.join(svmbir_lib_path, 'proj', object_name)
    paths['init_proj_name'] = os.path.join(svmbir_lib_path, 'init_proj', object_name)
    paths['prox_name'] = os.path.join(svmbir_lib_path, 'prox', object_name)

    paths['sysmatrix_name'] = os.path.join(svmbir_lib_path, 'sysmatrix', sysmatrix_name)

    paths['param_name'] = os.path.join(svmbir_lib_path, 'par', object_name)
    paths['sinoparams_fname'] = paths['param_name'] + '.sinoparams'
    paths['imgparams_fname'] = paths['param_name'] + '.imgparams'
    paths['reconparams_fname'] = paths['param_name'] + '.reconparams'
    paths['view_angle_list_fname'] = paths['param_name'] + '.ViewAngleList'

    paths['view_angle_list_name'] = object_name + '.ViewAngleList'

    return paths


def _transform_pyconv2c(**kwargs):
    ckwargs = dict()
    for key in kwargs :
        if key in _map_pyconv2camelcase.keys() :
            ckwargs[_map_pyconv2camelcase[key]] = kwargs[key]
        else :
            ckwargs[key] = kwargs[key]
    return ckwargs


def _gen_sysmatrix_c(sinoparams, imgparams, angles, settings):

    # Unpack the settings
    verbose = settings['verbose']
    svmbir_lib_path = settings['svmbir_lib_path']
    object_name = settings['object_name']

    # Get info needed for c
    hash_val, relevant_params = utils.hash_params(angles.astype(np.single), **{**sinoparams, **imgparams})

    # In this version we write data to disk, which is then read by c
    # Get info for writing to disk
    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val[:__namelen_sysmatrix])
    param_name = paths['param_name']
    sysmatrix_name = paths['sysmatrix_name']
    sinoparams_c = _transform_pyconv2c(**sinoparams)
    imgparams_c = _transform_pyconv2c(**imgparams)

    # Write to disk
    write_params(paths['sinoparams_fname'], **sinoparams_c)
    write_params(paths['imgparams_fname'], **imgparams_c)

    with open(paths['view_angle_list_fname'], 'w') as fileID :
        for angle in list(angles) :
            fileID.write(str(angle) + "\n")

    # Calculate the system matrix (or use existing if one exists)
    # In this version the matrix is saved to disk
    Amatrix_file = paths['sysmatrix_name'] + '.2Dsvmatrix'
    if os.path.exists(Amatrix_file) :
        if verbose > 0:
            print('Found system matrix: {}'.format(sysmatrix_name + '.2Dsvmatrix'))
        if os.access(Amatrix_file, os.W_OK):
            os.utime(Amatrix_file)  # update file modified time
    else :
        _cmd_exec(i=param_name, j=param_name, m=sysmatrix_name, v=str(verbose))

    # Return the sysmatrix (or info to get it in this case)
    return paths


##################################################################
# Items that are needed for command line interface
##################################################################

def _cmd_exec(exec_path = __exec_path__, *args, **kwargs):
    arg_list = [exec_path]
    for key in args :
        arg_list.append('-' + key)

    for key, value in kwargs.items() :
        arg_list.append('-' + key)
        arg_list.append(value)

    # print(arg_list)
    # os.environ['OMP_NUM_THREADS'] = '20'
    # os.environ['OMP_DYNAMIC'] = 'true'
    subprocess.run(arg_list)


##################################################################
# Items that could be converted to typed cython for interface to c
##################################################################

def _init_geometry( angles, num_channels, num_views, num_slices, num_rows, num_cols,
                    geometry, dist_source_detector, magnification,
                    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
                    svmbir_lib_path = __svmbir_lib_path, object_name = 'object'):

    sinoparams, imgparams, settings = utils.get_params_dicts(angles, num_channels, num_views, num_slices, num_rows, num_cols,
                    geometry, dist_source_detector, magnification,
                    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
                    svmbir_lib_path, object_name, interface='Command Line')

    # Then call c to get the system matrix - the output dict can be used to pass the matrix itself
    # and/or to pass path information to a file containing the matrix
    sysmatrix_struct = _gen_sysmatrix_c(sinoparams, imgparams, angles, settings)

    # Convert back to a form for python
    paths = sysmatrix_struct # This should be converted to use the matrix itself - right now it uses pathnames

    return paths, sinoparams, imgparams


def multires_recon(sino, angles, weights, weight_type, init_image, prox_image, init_proj,
                   geometry, dist_source_detector, magnification,
                   num_rows, num_cols, roi_radius, delta_channel, delta_pixel, center_offset,
                   sigma_y, sigma_x, p, q, T, b_interslice,
                   positivity, relax_factor, max_resolutions, stop_threshold, max_iterations,
                   num_threads, delete_temps, svmbir_lib_path, object_name, verbose):
    """Multi-resolution SVMBIR reconstruction used by svmbir.recon().

    Args: See svmbir.recon() for argument structure
    """

    # Determine if it the algorithm should reduce resolution further
    go_to_lower_resolution = (max_resolutions > 0) and (min(num_rows, num_cols) > 16)

    # If resolution is too high, then do recursive call to lower resolutions
    if go_to_lower_resolution:
        new_max_resolutions = max_resolutions-1;

        # Set the pixel pitch, num_rows, and num_cols for the next lower resolution
        lr_delta_pixel = 2 * delta_pixel
        lr_num_rows = int(np.ceil(num_rows / 2))
        lr_num_cols = int(np.ceil(num_cols / 2))

        # Rescale sigma_y for lower resolution
        lr_sigma_y = 2.0**0.5 * sigma_y

        # Reduce resolution of initialization image if there is one
        if isinstance(init_image, np.ndarray) and (init_image.ndim == 3):
            lr_init_image = utils.recon_resize(init_image, (lr_num_rows, lr_num_cols))
        else:
            lr_init_image = init_image

        # Reduce resolution of proximal image if there is one
        if isinstance(prox_image, np.ndarray) and (prox_image.ndim == 3):
            lr_prox_image = utils.recon_resize(prox_image, (lr_num_rows, lr_num_cols))
        else:
            lr_prox_image = prox_image

        if verbose >= 1:
            print(f'Calling multires_recon for axial size (rows,cols)=({lr_num_rows},{lr_num_cols}).')

        lr_recon = multires_recon(sino=sino, angles=angles, weights=weights, weight_type=weight_type,
                        geometry=geometry, dist_source_detector=dist_source_detector, magnification=magnification,
                        init_image=lr_init_image, prox_image=lr_prox_image, init_proj=init_proj,
                        num_rows=lr_num_rows, num_cols=lr_num_cols, roi_radius=roi_radius,
                        delta_channel=delta_channel, delta_pixel=lr_delta_pixel, center_offset=center_offset,
                        sigma_y=lr_sigma_y, sigma_x=sigma_x, p=p,q=q,T=T,b_interslice=b_interslice,
                        positivity=positivity, relax_factor=relax_factor, max_resolutions=new_max_resolutions,
                        stop_threshold=stop_threshold, max_iterations=max_iterations, num_threads=num_threads,
                        delete_temps=delete_temps, svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                        verbose=verbose)

        # Interpolate resolution of reconstruction
        new_init_image = utils.recon_resize(lr_recon, (num_rows, num_cols))
        del lr_recon

    # Perform reconstruction at current resolution
    if verbose >= 1 :
        print(f'Reconstructing axial size (rows,cols)=({num_rows},{num_cols}).')

    # Collect parameters to pass to C
    (num_views, num_slices, num_channels) = sino.shape

    if np.isscalar(init_image) :
        init_image_value = init_image
    else :
        init_image_value = 0

    reconparams = utils.get_reconparams_dicts(sigma_y, positivity, relax_factor, sigma_x, p, q, T, b_interslice,
                            stop_threshold, max_iterations,init_image_value=init_image_value, interface = 'Command Line')

    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
                                                  geometry=geometry, dist_source_detector=dist_source_detector,
                                                  magnification=magnification,
                                                  num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                  num_rows=num_rows, num_cols=num_cols,
                                                  delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                  roi_radius=roi_radius,
                                                  svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                  verbose=verbose)

    # Interface to disk and command line
    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'],
                    s=paths['sino_name'], r=paths['recon_name'], m=paths['sysmatrix_name'],
                    w=paths['wght_name'], v=str(verbose))

    # We're doing anything with projection of the output, so removing to save work
    # cmd_args['f'] = paths['proj_name']

    # Initializing initial conditon w/ multi-res result like this allows de-allocation
    if 'new_init_image' in locals():
        write_recon_openmbir(new_init_image, paths['init_name'] + '_slice', '.2Dimgdata')
        cmd_args['t'] = paths['init_name']
        del new_init_image
    elif not np.isscalar(init_image):
        write_recon_openmbir(init_image, paths['init_name'] + '_slice', '.2Dimgdata')
        cmd_args['t'] = paths['init_name']

    if init_proj is not None:
        write_sino_openmbir(init_proj, paths['init_proj_name'] + '_slice', '.2Dsinodata')
        cmd_args['e'] = paths['init_proj_name']

    if prox_image is not None:
        write_recon_openmbir(prox_image, paths['prox_name'] + '_slice', '.2Dimgdata')
        cmd_args['p'] = paths['prox_name']
        reconparams['prior_model'] = 'PandP'

    reconparams_c = _transform_pyconv2c(**reconparams)
    write_params(paths['reconparams_fname'], **reconparams_c)

    write_sino_openmbir(sino, paths['sino_name'] + '_slice', '.2Dsinodata')
    write_sino_openmbir(weights, paths['wght_name'] + '_slice', '.2Dweightdata')

    _cmd_exec(**cmd_args)

    x = read_recon_openmbir(paths['recon_name'] + '_slice', '.2Dimgdata',
                            imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    if delete_temps:
        os.remove(paths['sinoparams_fname'])
        os.remove(paths['imgparams_fname'])
        os.remove(paths['reconparams_fname'])
        os.remove(paths['view_angle_list_fname'])

        delete_data_openmbir(paths['recon_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['sino_name'] + '_slice', '.2Dsinodata', sinoparams['num_slices'])
        # delete_data_openmbir(paths['proj_name'] + '_slice', '.2Dprojection', sinoparams['num_slices'])
        delete_data_openmbir(paths['wght_name'] + '_slice', '.2Dweightdata', sinoparams['num_slices'])

        if 't' in cmd_args:
            delete_data_openmbir(paths['init_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])

        if init_proj is not None:
            delete_data_openmbir(paths['init_proj_name'] + '_slice', '.2Dprojection', sinoparams['num_slices'])

        if prox_image is not None:
            delete_data_openmbir(paths['prox_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])

    return x


def project(image, settings):
    """Forward projection function used by svmbir.project().

    Args:
        image (ndarray): 3D Image to be projected
        settings (dict): Dictionary containing projection settings

    Returns:
        TYPE: Description
    """

    paths = settings['paths']
    imgparams = settings['imgparams']
    sinoparams = settings['sinoparams']
    verbose = settings['verbose']
    delete_temps = settings['delete_temps']

    write_recon_openmbir(image, paths['recon_name'] + '_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
              f=paths['proj_name'], t=paths['recon_name'], v=str(verbose))

    proj = read_sino_openmbir(paths['proj_name'] + '_slice', '.2Dprojection',
                              sinoparams['num_views'], sinoparams['num_slices'], sinoparams['num_channels'])

    if delete_temps :
        os.remove(paths['sinoparams_fname'])
        os.remove(paths['imgparams_fname'])
        os.remove(paths['view_angle_list_fname'])

        delete_data_openmbir(paths['recon_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['proj_name'] + '_slice', '.2Dprojection', sinoparams['num_slices'])

    return proj


def backproject(sino, settings):
    """Back projection function used by svmbir.backproject().

    Args:
        sino (ndarray): 3D sinogram
        settings (dict): Dictionary containing back projection settings

    Returns:
        ndarray: Description
    """

    paths = settings['paths']
    verbose = settings['verbose']
    imgparams = settings['imgparams']
    sinoparams = settings['sinoparams']
    delete_temps = settings['delete_temps']

    write_sino_openmbir(sino, paths['sino_name'] + '_slice', '.2Dsinodata')

    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
                    s=paths['sino_name'], r=paths['recon_name'], v=str(verbose))

    cmd_opts = ['b']

    _cmd_exec(__exec_path__,*cmd_opts,**cmd_args)

    image = read_recon_openmbir(paths['recon_name'] + '_slice', '.2Dimgdata',
                                imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    if delete_temps :
        os.remove(paths['sinoparams_fname'])
        os.remove(paths['imgparams_fname'])
        os.remove(paths['view_angle_list_fname'])

        delete_data_openmbir(paths['recon_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['sino_name'] + '_slice', '.2Dsinodata', sinoparams['num_slices'])

    return image


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

    if len(x.shape) != 3:
        raise Exception("write_sino_openmbir(): Error! Input must be 3D")

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

    if len(x.shape) != 3:
        raise Exception("write_recon_openmbir(): Error! Input must be 3D")

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
