
import os
import shutil
import argparse
from glob import glob
import numpy as np
import subprocess
import math
import hashlib

from .utils import *

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__), 'sv-mbirct', 'bin', 'mbir_ct'))

__svmbir_lib_path = os.path.join(os.getenv('HOME'), '.cache', 'svmbir_lib')

__namelen_sysmatrix = 20

_default_reconparams = {'prior_model': 'QGGMRF',
    'init_image_value': 0.0001,
    'p': 1.2,
    'q': 2.0,
    'T': 1.0,
    'sigma_x': 0.01,
    'sigma_y': 1,
    'b_nearest': 1.0,
    'b_diag': 0.707,
    'b_interslice': 1.0,
    'stop_threshold': 0.0,
    'max_iterations': 20,
    'positivity': 1,
    'weight_type': 0} # constant weights

_map_pyconv2camelcase={'prior_model': 'PriorModel',
    'init_image_value': 'InitImageValue',
    'p': 'p',
    'q': 'q',
    'T': 'T',
    'sigma_x': 'SigmaX',
    'sigma_y': 'SigmaY',
    'b_nearest': 'b_nearest',
    'b_diag': 'b_diag',
    'b_interslice': 'b_interslice',
    'stop_threshold': 'StopThreshold',
    'max_iterations': 'MaxIterations',
    'positivity': 'Positivity',
    'weight_type': 'weightType',
    'geometry': 'Geometry',
    'num_channels': 'NChannels',
    'num_views': 'NViews',
    'num_slices': 'NSlices',
    'delta_channel': 'DeltaChannel',
    'center_offset': 'CenterOffset',
    'delta_slice': 'DeltaSlice',
    'first_slice_number': 'FirstSliceNumber',
    'view_angle_list': 'ViewAngleList',
    'delta_xy':'Deltaxy',
    'delta_z':'DeltaZ',
    'roi_radius':'ROIRadius'}


def _gen_paths(svmbir_lib_path=__svmbir_lib_path, object_name='object', sysmatrix_name='object'):

    os.makedirs( os.path.join(svmbir_lib_path,'obj'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'sino'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'weight'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'recon'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'init'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'proj'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'init_proj'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'prox'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'sysmatrix'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'par'), exist_ok=True)

    paths = dict()
    paths['sino_name'] = os.path.join(svmbir_lib_path,'sino',object_name)
    paths['wght_name'] = os.path.join(svmbir_lib_path,'weight',object_name)
    paths['recon_name'] = os.path.join(svmbir_lib_path,'recon',object_name)
    paths['init_name'] = os.path.join(svmbir_lib_path,'init',object_name)
    paths['proj_name'] = os.path.join(svmbir_lib_path,'proj',object_name)
    paths['init_proj_name'] = os.path.join(svmbir_lib_path,'init_proj',object_name)
    paths['prox_name'] = os.path.join(svmbir_lib_path,'prox',object_name)
    
    paths['sysmatrix_name'] = os.path.join(svmbir_lib_path,'sysmatrix',sysmatrix_name)
    
    paths['param_name'] = os.path.join(svmbir_lib_path,'par',object_name)
    paths['sinoparams_fname'] = paths['param_name']+'.sinoparams'
    paths['imgparams_fname'] = paths['param_name']+'.imgparams'
    paths['reconparams_fname'] = paths['param_name']+'.reconparams'
    paths['view_angle_list_fname'] = paths['param_name']+'.ViewAngleList'

    paths['view_angle_list_name'] = object_name+'.ViewAngleList'

    return paths


def _transform_pyconv2c(**kwargs):
    ckwargs=dict()
    for key in kwargs:
        if key in _map_pyconv2camelcase.keys():
            ckwargs[_map_pyconv2camelcase[key]]=kwargs[key]
        else:
            ckwargs[key]=kwargs[key]
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

    hash_input = str(relevant_params)+str(np.around(angles, decimals=6) )

    hash_val = hashlib.sha512(hash_input.encode()).hexdigest()

    return hash_val, relevant_params


def _cmd_exec(exec_path=__exec_path__, *args, **kwargs):

    arg_list = [exec_path]
    for key in args:
        arg_list.append('-'+key)

    for key,value in kwargs.items():
        arg_list.append('-'+key)
        arg_list.append(value)

    # print(arg_list)
    # os.environ['OMP_NUM_THREADS'] = '20'
    # os.environ['OMP_DYNAMIC'] = 'true'
    subprocess.run(arg_list)


def _gen_sysmatrix(param_name, sysmatrix_name):

    if os.path.exists(sysmatrix_name+'.2Dsvmatrix'):
        print('Found system matrix: {}'.format(sysmatrix_name+'.2Dsvmatrix'))
    else:
        _cmd_exec(i=param_name, j=param_name, m=sysmatrix_name)


def _init_geometry(angles, num_channels, num_views, num_slices, num_rows, num_cols,
    delta_channel, delta_pixel, roi_radius, center_offset, 
    svmbir_lib_path=__svmbir_lib_path, object_name='object'):

    sinoparams = dict()
    sinoparams['geometry']= '3DPARALLEL'
    sinoparams['num_channels'] = num_channels
    sinoparams['num_views'] = num_views
    sinoparams['num_slices'] = num_slices
    sinoparams['delta_channel'] = delta_channel
    sinoparams['center_offset'] = center_offset
    sinoparams['delta_slice'] = 1
    sinoparams['first_slice_number'] = 0
    sinoparams['view_angle_list'] = object_name+'.ViewAngleList'

    imgparams = dict()
    imgparams['Nx'] = num_rows
    imgparams['Ny'] =  num_cols
    imgparams['Nz'] =  num_slices
    imgparams['first_slice_number'] = 0
    imgparams['delta_xy'] = delta_pixel
    imgparams['delta_z'] = 1
    imgparams['roi_radius'] = roi_radius

    hash_val, relevant_params = _hash_params(angles, **{**sinoparams, **imgparams})

    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val[:__namelen_sysmatrix])
    sinoparams_c=_transform_pyconv2c(**sinoparams)
    imgparams_c=_transform_pyconv2c(**imgparams)

    write_params(paths['sinoparams_fname'], **sinoparams_c)
    write_params(paths['imgparams_fname'], **imgparams_c)

    with open(paths['view_angle_list_fname'],'w') as fileID:
        for angle in list(angles):
            fileID.write(str(angle)+"\n")

    _gen_sysmatrix(paths['param_name'], paths['sysmatrix_name'])

    return paths, sinoparams, imgparams


def _calc_weights(sino, weight_type):

    if weight_type=='unweighted':
        weights = np.ones(sino.shape)
    elif weight_type=='transmission':
        weights = np.exp(-sino)
    elif weight_type=='transmission_root':
        weights = np.exp(-sino/2)
    elif weight_type=='emmission':
        weights = 1/(sino + 0.1)
    else:
        raise Exception("calc_weights: undefined weight_type {}".format(weight_type))

    return weights


def _auto_sigma_y(sino, weights, snr_db=30.0):

    signal_rms = np.mean(weights * sino**2)**0.5
    rel_noise_std = 10**(-snr_db/20)
    sigma_y = rel_noise_std * signal_rms

    return sigma_y


def _auto_sigma_x(sino, delta_channel=1.0, sharpen=1.0):

    (num_views, num_slices, num_channels) = sino.shape
    sigma_x = 0.1 * sharpen * np.mean(sino) / (num_channels*delta_channel)

    return sigma_x


def recon(sino, angles,
        center_offset=0.0, delta_channel=1.0, delta_pixel=1.0,
        num_rows=None, num_cols=None, roi_radius=None,
        sigma_y=None, snr_db=30.0, weights=None, weight_type='unweighted',
        sigma_x=None, sharpen=1.0,
        positivity=True, p=1.2, q=2.0, T=1.0, b_interslice=1.0, 
        init_image=0.0001, init_proj=None, prox_image=None,
        stop_threshold=0.0, max_iterations=20,
        num_threads=1, delete_temps=True, svmbir_lib_path=__svmbir_lib_path, object_name='object'):
    """ Computes the 3D MBIR reconstruction using a parallel beam geometry and other parameters as described below.
    
    Args:
        sino (ndarray): 3D numpy array of sinogram data with shape (num_view,num_slice,num_channel)
        angles (ndarray): 1D numpy array of view angles in radians. 
        center_offset (float, optional): Scalar value of offset from center-of-rotation.
        delta_channel (float, optional): Scalar value of detector channel spacing in ALU.
        delta_pixel (float, optional): Scalar value of the spacing between image pixels in the 2D slice plane in ALU.
        num_rows (None, optional): Integer number of rows in reconstructed image. If None, automatically set.
        num_cols (None, optional): Integer number of columns in reconstructed image. If None, automatically set.
        roi_radius (None, optional): Description
        sigma_y (None, optional): Description
        snr_db (float, optional): Description
        weights (None, optional): Description
        weight_type (str, optional): Description
        sigma_x (None, optional): Description
        sharpen (float, optional): Description
        positivity (bool, optional): Description
        p (float, optional): Description
        q (float, optional): Description
        T (float, optional): Description
        b_interslice (float, optional): Description
        init_image (float, optional): Description
        init_proj (None, optional): Description
        prox_image (None, optional): Description
        stop_threshold (float, optional): Description
        max_iterations (int, optional): Description
        num_threads (int, optional): Description
        delete_temps (bool, optional): Description
        svmbir_lib_path (TYPE, optional): Description
        object_name (str, optional): Description
    
    Returns:
        ndarray: Reconstructed 3D object.
    """
    print('Running Reconstruction ----------------------------')

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    (num_views, num_slices, num_channels) = sino.shape

    if num_rows is None:
        num_rows = int(np.ceil(num_channels*delta_channel/delta_pixel))

    if num_cols is None:
        num_cols = int(np.ceil(num_channels*delta_channel/delta_pixel))

    if roi_radius is None:
        roi_radius = float(delta_pixel * max(num_rows,num_cols))

    if weights is None:
        weights = _calc_weights(sino, weight_type)

    if sigma_y is None:
        sigma_y = _auto_sigma_y(sino, weights, snr_db)

    if sigma_x is None:
        sigma_x = _auto_sigma_x(sino, delta_channel, sharpen)

    if np.isscalar(init_image):
        init_image = init_image*np.ones((num_slices, num_rows, num_cols))


    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
        num_channels=num_channels, num_views=num_views, num_slices=num_slices, 
        num_rows=num_rows, num_cols=num_cols, 
        delta_channel=delta_channel, delta_pixel=delta_pixel, roi_radius=roi_radius,
        svmbir_lib_path=svmbir_lib_path, object_name=object_name)

    reconparams = parse_params(_default_reconparams, p=p, q=q, T=T, sigma_x=sigma_x,
        b_interslice=b_interslice, stop_threshold=stop_threshold, max_iterations=max_iterations,
        positivity=int(positivity))
    
    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
    s=paths['sino_name'], f=paths['proj_name'], w=paths['wght_name'],
    r=paths['recon_name'],
    m=paths['sysmatrix_name'],
    t=paths['init_name'])

    if init_proj is not None:
        write_sino_openmbir(init_proj, paths['init_proj_name']+'_slice', '.2Dsinodata')
        cmd_args['e'] = paths['init_proj_name']

    if prox_image is not None:
        write_recon_openmbir(prox_image, paths['prox_name']+'_slice', '.2Dimgdata')
        cmd_args['p'] = paths['prox_name']
        reconparams['prior_model'] = 'PandP'

    reconparams_c=_transform_pyconv2c(**reconparams)
    write_params(paths['reconparams_fname'], **reconparams_c)

    write_sino_openmbir(sino, paths['sino_name']+'_slice', '.2Dsinodata')
    write_sino_openmbir(weights/sigma_y**2, paths['wght_name']+'_slice', '.2Dweightdata')
    write_recon_openmbir(init_image, paths['init_name']+'_slice', '.2Dimgdata')

    _cmd_exec(**cmd_args)

    x = read_recon_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', 
        imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    if delete_temps:
        os.remove( paths['sinoparams_fname'] )
        os.remove( paths['imgparams_fname'] )
        os.remove( paths['reconparams_fname'] )
        os.remove( paths['view_angle_list_fname'] )

        delete_data_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['sino_name']+'_slice', '.2Dsinodata', sinoparams['num_slices'])
        delete_data_openmbir(paths['proj_name']+'_slice', '.2Dprojection', sinoparams['num_slices'])
        delete_data_openmbir(paths['wght_name']+'_slice', '.2Dweightdata', sinoparams['num_slices'])
        delete_data_openmbir(paths['init_name']+'_slice', '.2Dimgdata', imgparams['Nz'])

        if init_proj is not None:
            delete_data_openmbir(paths['init_proj_name']+'_slice', '.2Dprojection', sinoparams['num_slices'])

        if prox_image is not None:
            delete_data_openmbir(paths['prox_name']+'_slice', '.2Dimgdata', imgparams['Nz'])

    return x


def project(angles, image, num_channels,
        delta_channel=1.0, delta_pixel=1.0, center_offset=0.0, roi_radius=None,
        num_threads=1, delete_temps=True, svmbir_lib_path=__svmbir_lib_path, object_name='object'):

    print('Running Forward projection ----------------------------')

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    num_slices = image.shape[0]
    num_rows = image.shape[1]
    num_cols = image.shape[2]
    num_views = len(angles)

    if roi_radius is None:
        roi_radius = float(delta_pixel * max(num_rows,num_cols))

    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
        num_channels=num_channels, num_views=num_views, num_slices=num_slices, 
        num_rows=num_rows, num_cols=num_cols, 
        delta_channel=delta_channel, delta_pixel=delta_pixel, roi_radius=roi_radius,
        svmbir_lib_path=svmbir_lib_path, object_name=object_name)

    write_recon_openmbir(image, paths['recon_name']+'_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'])

    proj = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection', 
        sinoparams['num_views'], sinoparams['num_slices'], sinoparams['num_channels'])

    if delete_temps:
        os.remove( paths['sinoparams_fname'] )
        os.remove( paths['imgparams_fname'] )
        os.remove( paths['view_angle_list_fname'] )

        delete_data_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['proj_name']+'_slice', '.2Dprojection', sinoparams['num_slices'])

    return proj


def clear_cache(svmbir_lib_path=__svmbir_lib_path):
    shutil.rmtree(svmbir_lib_path)

