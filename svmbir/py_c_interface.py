# -*- coding: utf-8 -*-
# Copyright (C) by
# All rights reserved. 

# These imports are needed only for read/write and command line interfaces
import subprocess
import shutil
import os
import hashlib
from ._utils import *

"""
Overview: 
"""

##################################################################
# Items that are needed for read/write to disk interface
##################################################################

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__), 'sv-mbirct', 'bin', 'mbir_ct'))

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

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
                         'weight_type' : 'weightType',
                         'geometry' : 'Geometry',
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


def _svmbir_lib_path():
    return __svmbir_lib_path


def _clear_cache(svmbir_lib_path = __svmbir_lib_path):
    shutil.rmtree(svmbir_lib_path)


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


def _hash_params(angles, **kwargs):
    relevant_params = dict()
    relevant_params['Nx'] = kwargs['Nx']
    relevant_params['Ny'] = kwargs['Ny']
    relevant_params['delta_xy'] = kwargs['delta_xy']
    relevant_params['roi_radius'] = kwargs['roi_radius']
    relevant_params['num_channels'] = kwargs['num_channels']
    relevant_params['num_views'] = kwargs['num_views']
    relevant_params['delta_channel'] = kwargs['delta_channel']
    relevant_params['center_offset'] = kwargs['center_offset']

    hash_input = str(relevant_params) + str(np.around(angles, decimals=6))

    hash_val = hashlib.sha512(hash_input.encode()).hexdigest()

    return hash_val, relevant_params

def _gen_sysmatrix_c(sinoparams, imgparams, angles, settings):

    # Unpack the settings
    verbose = settings['verbose']
    svmbir_lib_path = settings['svmbir_lib_path']
    object_name = settings['object_name']

    # Get info needed for c
    hash_val, relevant_params = _hash_params(angles, **{**sinoparams, **imgparams})

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
    if os.path.exists(sysmatrix_name + '.2Dsvmatrix') :
        print('Found system matrix: {}'.format(sysmatrix_name + '.2Dsvmatrix'))
        os.utime(sysmatrix_name + '.2Dsvmatrix')  # update file modified time
    else :
        _cmd_exec(i=param_name, j=param_name, m=sysmatrix_name, v=str(verbose))

    # Return the sysmatrix (or info to get it in this case)
    return paths

##################################################################
# Items with interface to read/write and command line
##################################################################


def _fixed_res_recon_c(reconparams, imgparams, sinoparams, data, settings):
    # Unpack the data
    init_image = data['init_image']
    init_proj = data['init_proj']
    prox_image = data['prox_image']
    sino = data['sino']
    weights = data['weights']

    # Unpack the settings
    verbose = settings['verbose']
    paths = settings['paths']
    delete_temps = settings['delete_temps']

    # Interface to disk and command line
    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'],
                    s=paths['sino_name'], r=paths['recon_name'], m=paths['sysmatrix_name'],
                    w=paths['wght_name'], f=paths['proj_name'], v=str(verbose))

    if not np.isscalar(init_image):
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
        delete_data_openmbir(paths['proj_name'] + '_slice', '.2Dprojection', sinoparams['num_slices'])
        delete_data_openmbir(paths['wght_name'] + '_slice', '.2Dweightdata', sinoparams['num_slices'])

        if not np.isscalar(init_image):
            delete_data_openmbir(paths['init_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])

        if init_proj is not None:
            delete_data_openmbir(paths['init_proj_name'] + '_slice', '.2Dprojection', sinoparams['num_slices'])

        if prox_image is not None:
            delete_data_openmbir(paths['prox_name'] + '_slice', '.2Dimgdata', imgparams['Nz'])

    return x


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
                    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
                    svmbir_lib_path = __svmbir_lib_path, object_name = 'object'):

    # Collect the information needed to pass to c
    # - ideally these should be put in a struct that could be used by c directly
    # First the sinogram parameters
    sinoparams = dict()
    sinoparams['geometry'] = '3DPARALLEL'
    sinoparams['num_channels'] = num_channels
    sinoparams['num_views'] = num_views
    sinoparams['num_slices'] = num_slices
    sinoparams['delta_channel'] = delta_channel
    sinoparams['center_offset'] = center_offset
    sinoparams['delta_slice'] = 1
    sinoparams['first_slice_number'] = 0
    sinoparams['view_angle_list'] = object_name + '.ViewAngleList'

    # Then the image parameters
    imgparams = dict()
    imgparams['Nx'] = num_cols
    imgparams['Ny'] = num_rows
    imgparams['Nz'] = num_slices
    imgparams['first_slice_number'] = 0
    imgparams['delta_xy'] = delta_pixel
    imgparams['delta_z'] = 1
    imgparams['roi_radius'] = roi_radius

    # Collect any info needed for c subroutine
    settings = dict()
    settings['verbose'] = verbose
    settings['svmbir_lib_path'] = svmbir_lib_path
    settings['object_name'] = object_name

    # Then call c to get the system matrix - the output dict can be used to pass the matrix itself
    # and/or to pass path information to a file containing the matrix
    sysmatrix_struct = _gen_sysmatrix_c(sinoparams, imgparams, angles, settings)

    # Convert back to a form for python
    paths = sysmatrix_struct # This should be converted to use the matrix itself - right now it uses pathnames

    return paths, sinoparams, imgparams


def fixed_resolution_recon(sino, angles,
                            center_offset, delta_channel, delta_pixel,
                            num_rows, num_cols, roi_radius,
                            sigma_y, snr_db, weights, weight_type,
                            sharpness, positivity, sigma_x, p, q, T, b_interslice,
                            init_image, prox_image, init_proj,
                            stop_threshold, max_iterations,
                            delete_temps, svmbir_lib_path, object_name,
                            verbose):
    """Fixed resolution SVMBIR reconstruction used by recon().

    Args: See recon() for argument structure
    """

    # Collect parameters to pass to C
    (num_views, num_slices, num_channels) = sino.shape

    if np.isscalar(init_image) :
        init_image_value = init_image
    else :
        init_image_value = 0

    reconparams = dict()
    reconparams['prior_model'] = 'QGGMRF'
    reconparams['init_image_value'] = init_image_value
    reconparams['p'] = p
    reconparams['q'] = q
    reconparams['T'] = T
    reconparams['sigma_x'] = sigma_x
    reconparams['sigma_y'] = sigma_y
    reconparams['b_nearest'] = 1.0
    reconparams['b_diag'] = 0.707
    reconparams['b_interslice'] = b_interslice
    reconparams['stop_threshold'] = stop_threshold
    reconparams['max_iterations'] = max_iterations
    reconparams['positivity'] = int(positivity)
    reconparams['weight_type'] = 'unweighted'  # constant weights

    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
                                                  num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                  num_rows=num_rows, num_cols=num_cols,
                                                  delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                  roi_radius=roi_radius,
                                                  svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                  verbose=verbose)
    # Collect data and settings to pass to c
    data = dict()
    data['init_image'] = init_image
    data['init_proj'] = init_proj
    data['prox_image'] = prox_image
    data['sino'] = sino
    data['weights'] = weights

    settings = dict()
    settings['verbose'] = verbose
    settings['paths'] = paths
    settings['delete_temps'] = delete_temps

    # Do the recon
    x = _fixed_res_recon_c(reconparams, imgparams, sinoparams, data, settings)

    return x


def project(image, sinoparams, settings):

    paths = settings['paths']
    verbose = settings['verbose']
    imgparams = settings['imgparams']
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
