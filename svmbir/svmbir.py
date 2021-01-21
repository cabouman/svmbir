# -*- coding: utf-8 -*-
# Copyright (C) by
# All rights reserved.

import math
from psutil import cpu_count
import shutil
from skimage.transform import resize  # Do we need to choose this more carefully?
import numpy as np
import os
import svmbir._utils as utils
if os.environ.get('CLIB') =='CMD_LINE':
    import svmbir.interface_py_c as ci
else:
    import svmbir.interface_cy_c as ci

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

def _svmbir_lib_path():
    """Returns the path to the cache directory used by svmbir
    """
    return __svmbir_lib_path


def _clear_cache(svmbir_lib_path = __svmbir_lib_path):
    """Clears the cache files used by svmbir
    
    Args:
        svmbir_lib_path (string): Path to svmbir cache directory. Defaults to __svmbir_lib_path variable
    """
    shutil.rmtree(svmbir_lib_path)


def calc_weights(sino, weight_type ):
    """Computes the weights used in MBIR reconstruction.

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
    if weight_type == 'unweighted' :
        weights = np.ones(sino.shape)
    elif weight_type == 'transmission' :
        weights = np.exp(-sino)
    elif weight_type == 'transmission_root' :
        weights = np.exp(-sino / 2)
    elif weight_type == 'emission' :
        weights = 1 / (sino + 0.1)
    else :
        raise Exception("calc_weights: undefined weight_type {}".format(weight_type))

    return weights


def auto_sigma_y(sino, weights, snr_db = 30.0, delta_pixel = 1.0, delta_channel = 1.0):
    """Computes the automatic value of ``sigma_y`` for use in MBIR reconstruction.

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
    # Compute indicator function for sinogram support
    sino_indicator = _sino_indicator(sino)

    # compute RMS value of sinogram excluding empty space
    signal_rms = np.average(weights * sino ** 2, None, sino_indicator) ** 0.5

    # convert snr to relative noise standard deviation
    rel_noise_std = 10 ** (-snr_db / 20)

    # compute sigma_y and scale by relative pixel and detector pitch
    sigma_y = rel_noise_std * signal_rms * (delta_pixel / delta_channel) ** (0.5)

    return sigma_y


def auto_sigma_x(sino, delta_channel = 1.0, sharpness = 1.0 ):
    """Computes the automatic value of ``sigma_x`` for use in MBIR reconstruction.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness

    Returns:
        float: Automatic value of regularization parameter.
    """
    (num_views, num_slices, num_channels) = sino.shape

    # Compute indicator function for sinogram support
    sino_indicator = _sino_indicator(sino)

    # Compute a typical image value by dividing average sinogram value by a typical projection path length
    typical_img_value = np.average(sino, weights=sino_indicator) / (num_channels * delta_channel)

    # Compute sigma_x as a fraction of the typical image value
    sigma_x = 0.2 * (2 ** sharpness) * typical_img_value

    return sigma_x


def auto_num_rows(num_channels, delta_channel, delta_pixel):
    """Computes the automatic value of ``num_rows``.
    """
    num_rows = int(np.ceil(num_channels * delta_channel / delta_pixel))
    return num_rows


def auto_num_cols(num_channels, delta_channel, delta_pixel):
    """Computes the automatic value of ``num_cols``.
    """
    num_cols = int(np.ceil(num_channels * delta_channel / delta_pixel))
    return num_cols


def auto_roi_radius(delta_pixel, num_rows, num_cols):
    """Computes the automatic value of ``roi_radius``.
       Chosen so that it inscribes the largest axis of the recon image.
    """
    roi_radius = float(delta_pixel * max(num_rows, num_cols))/2.0
    return roi_radius


def recon(sino, angles,
           center_offset = 0.0, delta_channel = 1.0, delta_pixel = 1.0,
           num_rows = None, num_cols = None, roi_radius = None,
           sigma_y = None, snr_db = 30.0, weights = None, weight_type = 'unweighted',
           sharpness = 1.0, positivity = True, sigma_x = None, p = 1.2, q = 2.0, T = 1.0, b_interslice = 1.0,
           init_image = 0.0, prox_image = None, init_proj = None,
           max_resolutions = 0, stop_threshold = 0.02, max_iterations = 100,
           num_threads = None, delete_temps = True, svmbir_lib_path = __svmbir_lib_path, object_name = 'object',
           verbose = 1) :
    """Computes 3D parallel beam MBIR reconstruction using multi-resolution SVMBIR algorithm.

    Args:
        sino (ndarray): 3D sinogram array with shape (num_views, num_slices, num_channels)

        angles (ndarray): 1D view angles array in radians.

        center_offset (float, optional): [Default=0.0] Scalar value of offset from center-of-rotation.

        delta_channel (float, optional): [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.

        delta_pixel (float, optional): [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in :math:`ALU`.

        num_rows (int, optional): [Default=None] Integer number of rows in reconstructed image.
            If None, automatically set.

        num_cols (int, optional): [Default=None] Integer number of columns in reconstructed image.
            If None, automatically set.

        roi_radius (float, optional): [Default=None] Scalar value of radius of reconstruction in :math:`ALU`.
            If None, automatically set with auto_roi_radius().
            Pixels outside the radius roi_radius in the :math:`(x,y)` plane are disregarded in the reconstruction.

        sigma_y (float, optional): [Default=None] Scalar value of noise standard deviation parameter.
            If None, automatically set with auto_sigma_y.

        snr_db (float, optional): [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB.
            Ignored if sigma_y is not None.

        weights (ndarray, optional): [Default=None] 3D weights array with same shape as sino.

        weight_type (string, optional): [Default="unweighted"] Type of noise model used for data.
            If the ``weights`` array is not supplied, then the function ``svmbir.calc_weights`` is used to set weights using specified ``weight_type`` parameter.
            Option "unweighted" corresponds to unweighted reconstruction;
            Option "transmission" is the correct weighting for transmission CT with constant dosage;
            Option "transmission_root" is commonly used with transmission CT data to improve image homogeneity;
            Option "emission" is appropriate for emission CT data.

        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.
            Ignored if sigma_x is not None.

        positivity (bool, optional): [Default=True] Boolean value that determines if positivity constraint is enforced. The positivity parameter defaults to True; however, it should be changed to False when used in applications that can generate negative image values.

        sigma_x (float, optional): [Default=None] Scalar value :math:`>0` that specifies the qGGMRF scale parameter.
            If None, automatically set with auto_sigma_x. The parameter sigma_x can be used to directly control regularization, but this is only recommended for expert users.

        p (float, optional): [Default=1.2] Scalar value in range :math:`[1,2]` that specifies the qGGMRF shape parameter.

        q (float, optional): [Default=2.0] Scalar value in range :math:`[p,1]` that specifies the qGGMRF shape parameter.

        T (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the qGGMRF threshold parameter.

        b_interslice (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the interslice regularization.
            The default value of 1.0 should be fine for most applications.
            However, b_interslice can be increased to values :math:`>1` in order to increase regularization along the slice axis.

        init_image (float, optional): [Default=0.0] Initial value of reconstruction image, specified by either a scalar value or a 3D numpy array with shape (num_slices,num_rows,num_cols).

        init_proj (None, optional): [Default=None] Initial value of forward projection of the init_image.
            This can be used to reduce computation for the first iteration when using the proximal map option.

        prox_image (ndarray, optional): [Default=None] 3D proximal map input image.
            If prox_image is supplied, then the proximal map prior model is used, and the qGGMRF parameters are ignored.

        stop_threshold (float, optional): [Default=0.02] Scalar valued stopping threshold in percent.
            If stop_threshold=0.0, then run max iterations.

        max_iterations (int, optional): [Default=100] Integer valued specifying the maximum number of iterations. The value of ``max_iterations`` may need to be increased for reconstructions with limited tilt angles or high regularization.

        max_resolutions (int, optional): [Default=0] Integer >=0 that specifies the maximum number of grid resolutions used to solve MBIR reconstruction problem.

        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system

        delete_temps (bool, optional): [Default=True] Delete temporary files used in computation.

        svmbir_lib_path (string, optional): [Default=~/.cache/svmbir/parbeam] Path to directory containing library of forward projection matrices.

        object_name (string, optional): [Default='object'] Specifies filenames of cached files.
            Can be changed suitably for running multiple instances of reconstructions.
            Useful for building multi-process and multi-node functionality on top of svmbir.

        verbose (int, optional): [Default=1] Possible values are {0,1,2}, where 0 is quiet, 1 prints minimal reconstruction progress information, and 2 prints the full information.

    Returns:
        3D numpy array: 3D reconstruction with shape (num_slices,num_rows,num_cols) in units of :math:`ALU^{-1}`.
    """


    ##################################################################
    # Perform error checking to make sure parameter values are valid #
    ##################################################################

    # If not specified, then set number of threads = to number of processors
    # This could get call multiple times recursively. Is that a problem?
    if num_threads is None :
        num_threads = cpu_count(logical=False)
    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    # Test for valid sino and angles structure. If sino is 2D, make it 3D
    sino = utils.test_params_line0(sino, angles)
    (num_views, num_slices, num_channels) = sino.shape

    # Tests parameters for valid types and values; print warnings if necessary; and return default values.
    center_offset, delta_channel, delta_pixel = utils.test_params_line1(center_offset, delta_channel, delta_pixel)
    num_rows, num_cols, roi_radius = utils.test_params_line2(num_rows, num_cols, roi_radius)
    sigma_y, snr_db, weights, weight_type = utils.test_params_line3(sigma_y, snr_db, weights, weight_type)
    sharpness, positivity, sigma_x = utils.test_params_line4(sharpness, positivity, sigma_x)
    p, q, T, b_interslice = utils.test_pqtb_values(p, q, T, b_interslice)
    init_image, prox_image, init_proj = utils.test_params_line5(init_image, prox_image, init_proj)
    max_resolutions, stop_threshold, max_iterations = utils.test_params_line6(max_resolutions, stop_threshold, max_iterations)
    num_threads, delete_temps, verbose = utils.test_params_line7(num_threads, delete_temps, verbose)

    # Set automatic values of num_rows, num_cols, and roi_radius
    if num_rows is None:
        num_rows = auto_num_rows(num_channels, delta_channel, delta_pixel)
    if num_cols is None:
        num_cols = auto_num_cols(num_channels, delta_channel, delta_pixel)
    if roi_radius is None:
        roi_radius = auto_roi_radius(delta_pixel, num_rows, num_cols)

    # Set automatic values for weights
    if weights is None:
        weights = calc_weights(sino, weight_type)

    # Set automatic value of sigma_y
    if sigma_y is None:
        sigma_y = auto_sigma_y(sino, weights, snr_db, delta_pixel=delta_pixel, delta_channel=delta_channel)

    # Set automatic value of sigma_x
    if sigma_x is None:
        sigma_x = auto_sigma_x(sino, delta_channel, sharpness)

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
            lr_init_image = recon_resize(init_image, (lr_num_rows, lr_num_cols))
        else:
            lr_init_image = init_image

        # Reduce resolution of proximal image if there is one
        if isinstance(prox_image, np.ndarray) and (prox_image.ndim == 3):
            lr_prox_image = recon_resize(prox_image, (lr_num_rows, lr_num_cols))
        else:
            lr_prox_image = prox_image

        if verbose >= 1:
            print(f'Calling multires_recon for axial size (rows,cols)=({lr_num_rows},{lr_num_cols}).')

        lr_recon = recon(sino=sino, angles=angles,
                         center_offset=center_offset, delta_channel=delta_channel, delta_pixel=lr_delta_pixel,
                         num_rows=lr_num_rows, num_cols=lr_num_cols, roi_radius=roi_radius,
                         sigma_y=lr_sigma_y, snr_db=snr_db, weights=weights, weight_type=weight_type,
                         sharpness=sharpness, positivity=positivity, sigma_x=sigma_x, p=p, q=q, T=T, b_interslice=b_interslice,
                         init_image=lr_init_image, prox_image=lr_prox_image, init_proj=init_proj,
                         stop_threshold=stop_threshold, max_iterations=max_iterations, max_resolutions=new_max_resolutions,
                         num_threads=num_threads, delete_temps=delete_temps, svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                         verbose=verbose)

        # Interpolate resolution of reconstruction
        init_image = recon_resize(lr_recon, (num_rows, num_cols))
        del lr_recon

    # Perform reconstruction at current resolution
    if verbose >= 1 :
        print(f'Calling recon for axial size (rows,cols)=({num_rows},{num_cols}).')

    reconstruction = ci.fixed_resolution_recon(sino=sino, angles=angles,
                                               center_offset=center_offset, delta_channel=delta_channel, delta_pixel=delta_pixel,
                                               num_rows=num_rows, num_cols=num_cols, roi_radius=roi_radius,
                                               sigma_y=sigma_y, snr_db=snr_db, weights=weights, weight_type=weight_type,
                                               sharpness=sharpness, positivity=positivity, sigma_x=sigma_x, p=p, q=q, T=T, b_interslice=b_interslice,
                                               init_image=init_image, prox_image=prox_image, init_proj=init_proj,
                                               stop_threshold=stop_threshold, max_iterations=max_iterations,
                                               delete_temps=delete_temps, svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                               verbose=verbose)

    return reconstruction



def project(angles, image, num_channels,
             delta_channel = 1.0, delta_pixel = 1.0, center_offset = 0.0, roi_radius = None,
             num_threads = None, delete_temps = True, svmbir_lib_path = __svmbir_lib_path, object_name = 'object',
             verbose = 1):
    """Computes 3D parallel beam forward-projection.

    Args:
        angles (ndarray):
            1D numpy array of view angles in radians.
            The 1D array is organized so that angles[k] is the angle in radians for view :math:`k`.
        image (ndarray):
            3D numpy array of image being forward projected.
            The image is a 3D image with a shape of (num_slices,num_row,num_col) where num_slices is the number of sinogram slices.
            The image should be 0 outside the ROI as defined by roi_radius (those pixel will be disregarded).
        num_channels (int):
            Integer number of sinogram channels.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional):
            [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in :math:`ALU`.
        center_offset (float, optional):
            [Default=0.0] Scalar value of offset from center-of-rotation.
        roi_radius (float, optional): [Default=None] Scalar value of radius of reconstruction in :math:`ALU`.
            If None, automatically set with auto_roi_radius().
            Pixels outside the radius roi_radius in the :math:`(x,y)` plane are disregarded in the forward projection.
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
    if num_threads is None :
        num_threads = cpu_count(logical=False)

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    num_slices = image.shape[0]
    num_rows = image.shape[1]
    num_cols = image.shape[2]
    num_views = len(angles)

    if roi_radius is None :
        roi_radius = float(delta_pixel * max(num_rows, num_cols))

    paths, sinoparams, imgparams = ci._init_geometry(angles, center_offset=center_offset,
                                                     num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                     num_rows=num_rows, num_cols=num_cols,
                                                     delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                     roi_radius=roi_radius,
                                                     svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                     verbose=verbose)

    # Collect settings to pass to C
    settings = dict()
    settings['paths'] = paths
    settings['verbose'] = verbose
    settings['imgparams'] = imgparams
    settings['delete_temps'] = delete_temps

    # Do the projection
    proj = ci.project(image, sinoparams, settings)

    return proj


def recon_resize(recon, output_shape):
    """Resizes a reconstruction 3D numpy array of shape (slices,rows,cols).

    Args:
        recon (ndarray): 3D numpy array containing reconstruction with shape (slices, rows, cols)
        output_shape (tuple): (num_rows, num_cols) shape of resized output

    Returns:
        ndarray: 3D numpy array containing interpolated reconstruction with shape (num_slices, num_rows, num_cols).
    """

    recon = np.transpose(recon, (1, 2, 0))
    recon = resize(recon, output_shape)
    recon = np.transpose(recon, (2, 0, 1))

    return recon


def _sino_indicator(sino):
    """Computes a binary function that indicates the region of sinogram support.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels)

    Returns:
        int8: A binary value: =1 within sinogram support; =0 outside sinogram support.
    """
    indicator = np.int8(sino > 0.05 * np.mean(np.fabs(sino)))  # for excluding empty space from average
    return indicator
