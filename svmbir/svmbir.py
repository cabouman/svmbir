import os
import shutil
import argparse
from glob import glob
import numpy as np
import subprocess
import math
import hashlib
from psutil import cpu_count
from ._utils import *

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__), 'sv-mbirct', 'bin', 'mbir_ct'))

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

__namelen_sysmatrix = 20


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


def _clear_cache(svmbir_lib_path=__svmbir_lib_path):
    shutil.rmtree(svmbir_lib_path)


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


def _gen_sysmatrix(param_name, sysmatrix_name, verbose):

    if os.path.exists(sysmatrix_name+'.2Dsvmatrix'):
        print('Found system matrix: {}'.format(sysmatrix_name+'.2Dsvmatrix'))
        os.utime(sysmatrix_name+'.2Dsvmatrix')  # update file modified time
    else:
        _cmd_exec(i=param_name, j=param_name, m=sysmatrix_name, v=str(verbose))


def _init_geometry(angles, num_channels, num_views, num_slices, num_rows, num_cols,
    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
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
    imgparams['Nx'] = num_cols
    imgparams['Ny'] = num_rows
    imgparams['Nz'] = num_slices
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

    _gen_sysmatrix(paths['param_name'], paths['sysmatrix_name'], verbose)

    return paths, sinoparams, imgparams


def calc_weights(sino, weight_type):
    """Computes the weights used in reconstruction.

    Args:
        sino (ndarray): 3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)
        weight_type (string):[Default=0] Type of noise model used for data.

            If weight_type="unweighted"        => weights = numpy.ones_like(sino)

            If weight_type="transmission"      => weights = numpy.exp(-sino)

            If weight_type="transmission_root" => weights = numpy.exp(-sino/2)

            If weight_type="emission"         => weights = 1/(sino + 0.1)

    Returns:
        ndarray: 3D numpy array of weights with same shape as sino.

    Raises:
        Exception: Description
    """
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


def auto_sigma_y(sino, weights, snr_db=30.0, delta_pixel=1.0, delta_channel=1.0):
    """Computes the automatic value of the regularization parameter ``sigma_y`` for use in MBIR reconstruction.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)
        weights (ndarray):
            3D numpy array of weights with same shape as sino.
            The parameters weights should be the same values as used in svmbir reconstruction.
        snr_db (float, optional):
            [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB.
        delta_pixel (float, optional):
            [Default=1.0] Scalar value of pixel spacing in :math:`ALU`.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.


    Returns:
        ndarray: Automatic values of regularization parameter.
    """
    # compute indicator for excluding empty space from sinogram
    indicator = np.int8(sino > 0.05*np.mean(np.fabs(sino)) )

    # compute RMS value of sinogram excluding empty space
    signal_rms = np.average(weights * sino**2, None, indicator)**0.5

    # convert snr to relative noise standard deviation
    rel_noise_std = 10**(-snr_db/20)

    # compute sigma_y and scale by relative pixel and detector pitch
    sigma_y = rel_noise_std * signal_rms * (delta_pixel / delta_channel)

    return sigma_y


def auto_sigma_x(sino, delta_channel=1.0, sharpness=1.0):
    """Computes the automatic value of the regularization parameters sigma_x for use in MBIR reconstruction.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness

    Returns:
        float: Automatic value of regularization parameter.
    """
    (num_views, num_slices, num_channels) = sino.shape

    #sigma_x = 0.1 * sharpness * np.mean(sino) / (num_channels*delta_channel)                           # Verions 1
    #sigma_x = 0.1 * sharpness * np.average(sino, weights=indicator) / (num_channels * delta_channel)   # Version 2
    indicator = np.int8(sino > 0.05*np.mean(np.fabs(sino)) )    # for excluding empty space from average
    sigma_x = 0.2 * (2 ** sharpness) * np.average(sino, weights=indicator) / (num_channels * delta_channel)

    return sigma_x


def recon(sino, angles,
          center_offset=0.0, delta_channel=1.0, delta_pixel=1.0,
          num_rows=None, num_cols=None, roi_radius=None,
          sigma_y=None, snr_db=30.0, weights=None, weight_type='unweighted',
          sigma_x=None, sharpness=1.0, positivity=True, p=1.2, q=2.0, T=1.0, b_interslice=1.0,
          init_image=0.0, init_proj=None, prox_image=None,
          stop_threshold=0.01, max_iterations=100,
          num_threads=None, delete_temps=True, svmbir_lib_path=__svmbir_lib_path, object_name='object',
          verbose=1):
    """
    Computes the 3D MBIR reconstruction using a parallel beam geometry and other parameters as described below.

    Args:
        sino (float): 3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)

        angles (float): 1D numpy array of view angles in radians.

        center_offset (float, optional): [Default=0.0] Scalar value of offset from center-of-rotation.

        delta_channel (float, optional): [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.

        delta_pixel (float, optional): [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in :math:`ALU`.

        num_rows (int, optional): [Default=None] Integer number of rows in reconstructed image.
            If None, automatically set.

        num_cols (int, optional): [Default=None] Integer number of columns in reconstructed image.
            If None, automatically set.

        roi_radius (float, optional): [Default=None] Scalar value of radius of reconstruction in :math:`ALU`.
            If None, automatically set.

        sigma_y (float, optional): [Default=None] Scalar value of noise standard deviation parameter.
            If None, automatically set.

        snr_db (float, optional): [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB.
            Ignored if sigma_y is not None.

        weights (ndarray, optional): [Default=None] 3D numpy array of weights with same shape as sino.

        weight_type (string, optional): [Default="unweighted"] Type of noise model used for data.
            If the ``weights`` array is not supplied, then the function ``svmbir.calc_weights`` is used to set weights using specified ``weight_type`` parameter.
            Option "unweighted" corresponds to unweighted reconstruction;
            Option "transmission" is the correct weighting for transmission CT with constant dosage;
            Option "transmission_root" is commonly used with transmission CT data to improve image homogeneity;
            Option "emmission" is appropriate for emission CT data.

        sigma_x (float, optional): [Default=None] Scalar value :math:`>0` that specifies the qGGMRF scale parameter.
            If None, automatically set by calling svmbir.auto_sigma_x. The parameter sigma_x can be used to directly control regularization, but this is only recommended for expert users.

        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.
            Ignored if sigma_x is not None.

        positivity (bool, optional): [Default=True] Boolean value that determines if positivity constraint is enforced. The positivity parameter defaults to True; however, it should be changed to False when used in applications that can generate negative image values.

        p (float, optional): [Default=1.2] Scalar value :math:`>1` that specifies the qGGMRF shape parameter.

        q (float, optional): [Default=2.0] Scalar value :math:`>p` that specifies the qGGMRF shape parameter.

        T (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the qGGMRF threshold parameter.

        b_interslice (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the interslice regularization.
            The default values of 1 should be fine for most applications.
            However, b_interslice can be increased to values :math:`>1` in order to increase regularization along the slice axis.

        init_image (float, optional): [Default=0.0] Initial value of reconstruction image, specified by either a scalar value or a 3D numpy array with shape (num_slices,num_rows,num_cols).

        init_proj (None, optional): [Default=None] Initial value of forward projection of the init_image.
            This can be used to reduce computation for the first iteration when using the proximal map option.

        prox_image (ndarray, optional): [Default=None] 3D numpy array with proximal map input image.
            If prox_image is supplied, then the proximal map prior model is used, and the qGGMRF parameters are ignored.

        stop_threshold (float, optional): [Default=0.01] Scalar valued stopping threshold in percent.
            If stop_threshold=0, then run max iterations.

        max_iterations (int, optional): [Default=100] Integer valued specifying the maximum number of iterations.
        The value of ``max_iterations`` may need to be increased for reconstructions with limited tilt angles or high regularization.

        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system

        delete_temps (bool, optional): [Default=True] Delete temporary files used in computation.

        svmbir_lib_path (string, optional): [Default=~/.cache/svmbir/parbeam] Path to directory containing library of forward projection matrices.

        object_name (string, optional): [Default='object'] Specifies filenames of cached files.
            Can be changed suitably for running multiple instances of reconstructions.
            Useful for building multi-process and multi-node functionality on top of svmbir.

        verbose (int, optional): [Default=1] Possible values are {0,1,2}, where 0 is quiet, 1 prints minimal reconstruction progress information, and 2 prints the full information.

    Returns:
        ndarray: 3D numpy array with shape (num_slices,num_rows,num_cols) containing the reconstructed 3D object in units of :math:`ALU^{-1}`.
    """

    if num_threads is None:
        num_threads = cpu_count(logical=False)

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    if sino.ndim == 2:
        sino = sino[:,np.newaxis,:]
        print("svmbir.recon() warning: Input sino array only 2D. Adding singleton dimension to slice index to make it 3D.")

    (num_views, num_slices, num_channels) = sino.shape

    if num_rows is None:
        num_rows = int(np.ceil(num_channels*delta_channel/delta_pixel))

    if num_cols is None:
        num_cols = int(np.ceil(num_channels*delta_channel/delta_pixel))

    if roi_radius is None:
        roi_radius = float(delta_pixel * max(num_rows,num_cols))

    if weights is None:
        weights = calc_weights(sino, weight_type)

    if sigma_y is None:
        sigma_y = auto_sigma_y(sino, weights, snr_db, delta_pixel=delta_pixel, delta_channel=delta_channel)

    if sigma_x is None:
        sigma_x = auto_sigma_x(sino, delta_channel, sharpness)

    if np.isscalar(init_image):
        init_image_value = init_image
    else:
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
        delta_channel=delta_channel, delta_pixel=delta_pixel, roi_radius=roi_radius,
        svmbir_lib_path=svmbir_lib_path, object_name=object_name, verbose=verbose)

    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'],
        s=paths['sino_name'], r=paths['recon_name'], m=paths['sysmatrix_name'],
        w=paths['wght_name'], f=paths['proj_name'], v=str(verbose))

    if not np.isscalar(init_image):
        write_recon_openmbir(init_image, paths['init_name']+'_slice', '.2Dimgdata')
        cmd_args['t'] = paths['init_name']

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
    write_sino_openmbir(weights, paths['wght_name']+'_slice', '.2Dweightdata')
    del weights

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

        if not np.isscalar(init_image):
            delete_data_openmbir(paths['init_name']+'_slice', '.2Dimgdata', imgparams['Nz'])

        if init_proj is not None:
            delete_data_openmbir(paths['init_proj_name']+'_slice', '.2Dprojection', sinoparams['num_slices'])

        if prox_image is not None:
            delete_data_openmbir(paths['prox_name']+'_slice', '.2Dimgdata', imgparams['Nz'])

    return x


def project(angles, image, num_channels,
        delta_channel=1.0, delta_pixel=1.0, center_offset=0.0, roi_radius=None,
        num_threads=None, delete_temps=True, svmbir_lib_path=__svmbir_lib_path, object_name='object',
        verbose=1):
    """Computes the parallel beam sinogram by forward-projecting a 3D numpy array image that represents the volumetric image.

    Args:
        angles (ndarray):
            1D numpy array of view angles in radians.
            The 1D array is organized so that angles[k] is the angle in radians for view :math:`k`.
        image (ndarray):
            3D numpy array of image being forward projected.
            The image is a 3D image with a shape of (num_slices,num_row,num_col) where num_slices is the number of sinogram slices.
            The image should be 0 outside the ROI as defined by roi_radius.
        num_channels (int):
            Integer number of sinogram channels.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional):
            [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in :math:`ALU`.
        center_offset (float, optional):
            [Default=0.0] Scalar value of offset from center-of-rotation.
        roi_radius (None, optional):
            [Default=None] Scalar value of radius of reconstruction in :math:`ALU`.
            If None, automatically set by calling svmbir.auto_roi_radius.
            Pixels outside the radius roi_radius in the :math:`(x,y)` plane are disregarded in forward projection.
            The automatically set size of roi_radius is choosen so that it inscribes the largest axis of the recon image with a shape (num_slices,num_row,num_col).
        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system
        delete_temps (bool, optional):
            [Default=True] Delete temporary files used in computation.
        svmbir_lib_path (string, optional):
            [Default=~/.cache/svmbir/parbeam] String containing path to directory containing library of forward projection matrices and temp file.
        object_name (string, optional):
            [Default='object'] Specifies filenames of cached files.
            Can be changed suitably for running multiple instances of forward projections.
            Useful for building multi-process and multi-node functionality on top of svmbir.
        verbose (int, optional): [Default=1] Set to 0 for quiet mode.

    Returns:
        ndarray: 3D numpy array containing sinogram with shape (num_views, num_slices, num_channels).
    """
    if num_threads is None:
        num_threads = cpu_count(logical=False)

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
        svmbir_lib_path=svmbir_lib_path, object_name=object_name, verbose=verbose)

    write_recon_openmbir(image, paths['recon_name']+'_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'], v=str(verbose))

    proj = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection',
        sinoparams['num_views'], sinoparams['num_slices'], sinoparams['num_channels'])

    if delete_temps:
        os.remove( paths['sinoparams_fname'] )
        os.remove( paths['imgparams_fname'] )
        os.remove( paths['view_angle_list_fname'] )

        delete_data_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['proj_name']+'_slice', '.2Dprojection', sinoparams['num_slices'])

    return proj
