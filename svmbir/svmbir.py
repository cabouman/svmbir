# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 by SVMBIR Developers
# All rights reserved. BSD 3-clause License.

from psutil import cpu_count
import shutil
import numpy as np
import os
import sys
import warnings
import svmbir._utils as utils

if os.environ.get('CLIB') == 'CMD_LINE':
    import svmbir.interface_py_c as ci
else:
    import svmbir.interface_cy_c as ci

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir')


def _svmbir_lib_path():
    """Returns the path to the cache directory used by svmbir
    """
    return utils._svmbir_lib_path()


__svmbir_lib_path = _svmbir_lib_path()


def _clear_cache(svmbir_lib_path = __svmbir_lib_path):
    """Clear the cache files used by svmbir.

    Args:
        svmbir_lib_path (string): Path to svmbir cache directory. Defaults to __svmbir_lib_path variable.
    """
    utils._clear_cache(svmbir_lib_path)


def sino_sort(sino, angles, weights=None):
    r"""Sort sinogram views (and sinogram weights if provided) so that view angles are in monotonically increasing order on the interval :math:`[0,2\pi)`.
        This function can be used to preprocess the sinogram data so that svmbir reconstruction is faster.
        The function may create additional arrays that increase memory usage.

    Args:
        sino (ndarray): 3D numpy array of unsorted sinogram data with shape (num_views, num_slices, num_channels)
        angles (ndarray): 1D unsorted array of view angles in radians.
        weights (ndarray, optional): [Default=None] 3D unsorted array of weights with same shape as sino.

    Returns:
        - A tuple (sino, angles) when weights=None
        - A tuple (sino, angles, weights) if weights is not None.

        The arrays are sorted along the view axis so that they have monotone increasing view angles in the interval :math:`[0,2\pi)`.
    """

    # Wrap the view angles modulo 2pi and sort
    angles = np.mod(angles, 2*np.pi)
    sorted_indices = np.argsort(angles)

    # Sort sino, angles, and weights (if any) to be in monotone increasing order
    sino = np.array(sino)[sorted_indices]
    sino = np.ascontiguousarray(sino) # ensure views are in sorted order in memory
    angles = angles[sorted_indices]
    angles = np.ascontiguousarray(angles)

    if weights is None:
        return sino, angles
    else:
        weights = np.array(weights)[sorted_indices]
        weights = np.ascontiguousarray(weights)
        return sino, angles, weights


def calc_weights(sino, weight_type ):
    """Compute the weights used in MBIR reconstruction.

    Args:
        sino (ndarray): 3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).
        weight_type (string): Type of noise model used for data.

            If weight_type="unweighted"        => weights = numpy.ones_like(sino)

            If weight_type="transmission"      => weights = numpy.exp(-sino)

            If weight_type="transmission_root" => weights = numpy.exp(-sino/2)

            If weight_type="emission"          => weights = 1/(numpy.abs(sino) + 0.1)

    Returns:
        ndarray: 3D numpy array of weights with same shape as sino.

    Raises:
        Exception: Description
    """
    if weight_type == 'unweighted' :
        weights = np.ones(sino.shape).astype(sino.dtype)
    elif weight_type == 'transmission' :
        weights = np.exp(-sino)
    elif weight_type == 'transmission_root' :
        weights = np.exp(-sino / 2)
    elif weight_type == 'emission' :
        weights = 1 / (np.absolute(sino)  + 0.1)
    else :
        raise Exception("calc_weights: undefined weight_type {}".format(weight_type))

    return weights


def auto_max_resolutions(init_image) :
    """Compute the automatic value of ``max_resolutions`` for use in MBIR reconstruction.

    Args:
        init_image (ndarray): Initial image for reconstruction.
    Returns:
        int: Automatic value of ``max_resolutions``.
    """
    # Default value of max_resolutions
    max_resolutions = 2
    if isinstance(init_image, np.ndarray) and (init_image.ndim == 3):
        #print('Init image present. Setting max_resolutions = 0.')
        max_resolutions = 0

    return max_resolutions


def auto_sigma_y(sino, weights, magnification = 1.0, delta_channel = 1.0, delta_pixel = 1.0, snr_db = 30.0 ) :
    """Compute the automatic value of ``sigma_y`` for use in MBIR reconstruction.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).
        weights (ndarray):
            3D numpy array of weights with same shape as sino.
            The parameters weights should be the same values as used in svmbir reconstruction.
        magnification (float):
            (fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional):
            [Default=1.0] Scalar value of pixel spacing in :math:`ALU`.
        snr_db (float, optional):
            [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB.


    Returns:
        ndarray: Automatic values of regularization parameter.
    """
    # Compute indicator function for sinogram support
    sino_indicator = _sino_indicator(sino)

    # compute RMS value of sinogram excluding empty space
    signal_rms = np.average(weights * sino ** 2, None, sino_indicator) ** 0.5

    # convert snr to relative noise standard deviation
    rel_noise_std = 10 ** (-snr_db / 20)

    # compute the default_pixel_pitch = the detector pixel pitch in the image plane given the magnification
    default_pixel_pitch = delta_channel / magnification

    # compute the image pixel pitch relative to the default.
    pixel_pitch_relative_to_default = delta_pixel / default_pixel_pitch

    # compute sigma_y and scale by relative pixel and detector pitch
    sigma_y = rel_noise_std * signal_rms * pixel_pitch_relative_to_default ** (0.5)

    if sigma_y > 0:
        return sigma_y
    else:
        return 1.0


def auto_sigma_x(sino, magnification = 1.0, delta_channel = 1.0, sharpness = 0.0 ):
    """Compute the automatic value of ``sigma_x`` for use in MBIR reconstruction.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).
        magnification (float):
            (fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.

    Returns:
        float: Automatic value of regularization parameter.
    """
    return 0.2 * auto_sigma_prior(sino, magnification, delta_channel, sharpness)


def auto_sigma_p(sino, magnification = 1.0, delta_channel = 1.0, sharpness = 0.0 ):
    """Compute the automatic value of ``sigma_p`` for use in proximal map estimation.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).
        magnification (float):
            (fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.

    Returns:
        float: Automatic value of regularization parameter.
    """
    return 1.0 * auto_sigma_prior(sino, magnification, delta_channel, sharpness)


def auto_sigma_prior(sino, magnification = 1.0, delta_channel = 1.0, sharpness = 0.0 ):
    """Compute the automatic value of prior model regularization term for use in MBIR reconstruction or proximal map estimation. This subroutine is called by ``auto_sigma_x`` in MBIR reconstruction, or ``auto_sigma_p`` in proximal map estimation.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).
        magnification (float):
            (fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional):
            [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.

    Returns:
        float: Automatic value of regularization parameter.
    """
    (num_views, num_slices, num_channels) = sino.shape

    # Compute indicator function for sinogram support
    sino_indicator = _sino_indicator(sino)

    # Compute a typical image value by dividing average sinogram value by a typical projection path length
    typical_img_value = np.average(sino, weights=sino_indicator) / (num_channels * delta_channel / magnification)

    # Compute sigma_p as the typical image value when sharpness==0
    sigma_prior = (2 ** sharpness) * typical_img_value

    return sigma_prior


def auto_img_size(num_channels, delta_channel, delta_pixel, magnification=1.0):
    "Compute the default image size"
    num_rows = int(np.ceil(num_channels * delta_channel / (delta_pixel*magnification) ))
    num_cols = num_rows
    return num_rows,num_cols


def auto_roi_radius(delta_pixel, num_rows, num_cols):
    """Compute the automatic value of ``roi_radius``.
       Chosen so that it inscribes the largest axis of the recon image.
    """
    roi_radius = float(delta_pixel * max(num_rows, num_cols))/2.0
    return roi_radius


def max_threads(num_threads, num_slices, num_rows, num_cols, positivity = True):
    """Compute the maximum recommended number of threads for stable convergence.

    Args:
        num_threads (int): Desired number of compute threads requested when executed.
        num_slices (int): Number of slices in reconstruction.
        num_rows (int): Integer number of rows in reconstructed image.
        num_cols (int): Integer number of columns in reconstructed image.
        positivity (bool, optional): [Default=True] Boolean value that determines if positivity constraint is enforced.

    Returns:
        int: Maximum recommended number of threads.
    """
    # Set the minimum average super-voxel distance used in simultaneous updates
    avg_SV_dist = 7.0
    super_voxel_width = 16

    # compute number of possible super-voxels
    number_of_possible_SVs = ( num_slices * num_rows*num_cols) / super_voxel_width**2

    # Set the maximum number of allowed threads
    max_threads = int( np.ceil( number_of_possible_SVs / ( (avg_SV_dist)**2 ) ) )
    if ( (num_threads > max_threads) and (positivity is False) ):
        num_threads = max_threads
        print("Warning: Reducing the number of threads to ",num_threads)
    return num_threads


def recon(sino, angles,
          geometry = 'parallel', dist_source_detector = None, magnification = None,
          weights = None, weight_type = 'unweighted', init_image = 0.0, prox_image = None, init_proj = None,
          num_rows = None, num_cols = None, roi_radius = None,
          delta_channel = 1.0, delta_pixel = None, center_offset = 0.0,
          sigma_y = None, snr_db = 30.0, sigma_x = None, sigma_p = None, p = 1.2, q = 2.0, T = 1.0, b_interslice = 1.0,
          sharpness = 0.0, positivity = True, relax_factor=1.0, max_resolutions = None, stop_threshold = 0.02, max_iterations = 100,
          num_threads = None, delete_temps = True, svmbir_lib_path = __svmbir_lib_path, object_name = 'object',
          verbose = 1, output_params_dict=None) :
    """recon(sino, angles, geometry = 'parallel', **kwargs)

    Compute 3D MBIR reconstruction using multi-resolution SVMBIR algorithm.

    Args:
        sino (ndarray): 3D sinogram array with shape (num_views, num_slices, num_channels).
        angles (ndarray): 1D view angles array in radians.
        geometry (string):
            [Default='parallel'] Scanner geometry: 'parallel', 'fan-curved', or 'fan-flat'. Note for fan geometries
            the ``dist_source_detector`` and ``magnification`` arguments must be specified.
        dist_source_detector (float):
            (Required for fan beam geometries only) Distance from X-ray focal spot to detectors, in :math:`ALU`.
        magnification (float):
            (Required for fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        weights (ndarray, optional): [Default=None] 3D weights array with same shape as sino.
        weight_type (string, optional): [Default="unweighted"] Type of noise model used for data.
            If the ``weights`` array is not supplied, then the function ``svmbir.calc_weights`` is
            used to set weights using specified ``weight_type`` parameter.
            Option "unweighted" corresponds to unweighted reconstruction;
            Option "transmission" is the correct weighting for transmission CT with constant dosage;
            Option "transmission_root" is commonly used with transmission CT data to improve image homogeneity;
            Option "emission" is appropriate for emission CT data.
        init_image (float, optional): [Default=0.0] Initial value of reconstruction image, specified
            by either a scalar value or a 3D numpy array with shape (num_slices,num_rows,num_cols).
        prox_image (ndarray, optional): [Default=None] 3D proximal map input image.
            If prox_image is supplied, then the proximal map prior model is used, and the qGGMRF parameters are ignored.
        init_proj (None, optional): [Default=None] Initial value of forward projection of the init_image.
            This can be used to reduce computation for the first iteration when using the proximal map option.
        num_rows (int, optional): [Default=None] Integer number of rows in reconstructed image.
            If None, automatically set.
        num_cols (int, optional): [Default=None] Integer number of columns in reconstructed image.
            If None, automatically set.
        roi_radius (float, optional): [Default=None] Scalar value of radius of reconstruction in :math:`ALU`.
            If None, automatically set with auto_roi_radius().
            Pixels outside the radius roi_radius in the :math:`(x,y)` plane are disregarded in the reconstruction.
        delta_channel (float, optional): [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional): Scalar value of the spacing between image pixels in the 2D slice
            plane in :math:`ALU`. Defaults to ``delta_channel`` for ``parallel`` beam geometry,
            and ``delta_channel``/``magnification`` for fan beam geometries.
        center_offset (float, optional): [Default=0.0] Scalar value of offset from center-of-rotation.
        sigma_y (float, optional): [Default=None] Scalar value of noise standard deviation parameter.
            If None, automatically set with auto_sigma_y.
        snr_db (float, optional): [Default=30.0] Scalar value that controls assumed signal-to-noise
            ratio of the data in dB. Ignored if sigma_y is not None.
        sigma_x (float, optional): [Default=None] Scalar value :math:`>0` that specifies the qGGMRF scale parameter.
            Ignored if prox_image is not None.
            If None and prox_image is also None, automatically set with auto_sigma_x. Regularization should
            be controled with the ``sharpness`` parameter, but ``sigma_x`` can be set directly by expert users.
        sigma_p (float, optional): [Default=None] Scalar value :math:`>0` that specifies the proximal map parameter.
            If None, automatically set with auto_sigma_p. Regularization should be controled with the
            ``sharpness`` parameter, but ``sigma_p`` can be set directly by expert users.
        p (float, optional): [Default=1.2] Scalar value in range :math:`[1,2]` that specifies the qGGMRF shape parameter.
        q (float, optional): [Default=2.0] Scalar value in range :math:`[p,2]` that specifies the qGGMRF shape parameter.
        T (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the qGGMRF threshold parameter.
        b_interslice (float, optional): [Default=1.0] Scalar value :math:`>0` that specifies the interslice regularization.
            The default value of 1.0 should be fine for most applications.
            However, b_interslice can be increased to values :math:`>1` in order to increase
            regularization along the slice axis.
        sharpness (float, optional):
            [Default=0.0] Scalar value that controls level of sharpness.
            ``sharpness=0.0`` is neutral; ``sharpness>0`` increases sharpness; ``sharpness<0`` reduces sharpness.
            Ignored if ``sigma_x`` is not None in qGGMRF mode, or if ``sigma_p`` is not None in proximal map mode.
        positivity (bool, optional): [Default=True] Boolean value that determines if positivity constraint
            is enforced. The positivity parameter defaults to True; however, it should be changed to False
            when used in applications that can generate negative image values.
        relax_factor (float, optional): [Default=1.0] Relaxation factor for pixel update. Valid range (0,2.0].
            Values in (0,1) produce under-relaxation (smaller step size); Values in (1,2] produce over-relaxation.
        max_resolutions (int, optional): [Default=None] Integer >=0 that specifies the maximum number of grid
            resolutions used to solve MBIR reconstruction problem.
            If None, automatically set with auto_max_resolutions to 0 if inital image is provided and 2 otherwise.
        stop_threshold (float, optional): [Default=0.02] Scalar valued stopping threshold in percent.
            If stop_threshold=0.0, then run max iterations.
        max_iterations (int, optional): [Default=100] Integer valued specifying the maximum number of
            iterations. The value of ``max_iterations`` may need to be increased for reconstructions with
            limited tilt angles or high regularization.
        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system.
        delete_temps (bool, optional): [Default=True] Delete temporary files used in computation.
        svmbir_lib_path (string, optional): [Default='~/.cache/svmbir'] Path to directory containing
            library of forward projection matrices.
        object_name (string, optional): [Default='object'] Specifies filenames of cached files.
            Can be changed suitably for running multiple instances of reconstructions.
            Useful for building multi-process and multi-node functionality on top of svmbir.
        verbose (int, optional): [Default=1] Possible values are {0,1,2}, where 0 is quiet,
            1 prints minimal reconstruction progress information, and 2 prints the full information.

    Returns:
        3D numpy array: 3D reconstruction with shape (num_slices,num_rows,num_cols) in units of :math:`ALU^{-1}`.
    """

    # Issue notice of change of default regularization for 1 or 2 release cycles
    #if snr_db is None:
    #    if new_reg_defaults is True:
    #        snr_db = 40.0
    #    else:
    #        snr_db = 30.0
    #        sys.stderr.write("SVMBIR v0.3.0 NOTICE of pending change in regularization:\n")
    #        sys.stderr.write("** Default image regularization and effect of 'sharpness' will change in the\n")
    #        sys.stderr.write("** next release. To apply the changes immediately supply the following argument:\n")
    #        sys.stderr.write("** svmbir.recon(...,new_reg_defaults=True)\n")

    # Issue warning that 'fan' geometry will be removed in the future (last valid version is v0.2.9)
    if geometry=='fan':
        geometry = 'fan-curved'
        warnings.warn("'fan' geometry will be removed in a future release. Fan beam geometry is now specified as either 'fan-curved' or 'fan-flat'. Defaulting to 'fan-curved'.",FutureWarning)

    # If not specified, then set number of threads = to number of processors
    if num_threads is None :
        num_threads = cpu_count(logical=False)

    # Test for valid sino and angles structure. If sino is 2D, make it 3D
    angles = utils.test_args_angles(angles)
    sino = utils.test_args_sino(sino, angles)
    (num_views, num_slices, num_channels) = sino.shape

    # Tests parameters for valid types and values; print warnings if necessary; and return default values.
    geom_dict = utils.test_args_geom(num_rows, num_cols, delta_pixel, roi_radius, delta_channel, center_offset,
                                     output_as_dict=True)
    recon_dict = utils.test_args_recon(sharpness, positivity, relax_factor, max_resolutions, stop_threshold,
                                       max_iterations, output_as_dict=True)
    inits_dict = utils.test_args_inits(init_image, prox_image, init_proj, weights, weight_type,
                                       output_as_dict=True)
    noise_dict = utils.test_args_noise(sigma_y, snr_db, sigma_x, sigma_p, output_as_dict=True)
    qggmrf_dict = utils.test_args_qggmrf(p, q, T, b_interslice, output_as_dict=True)
    sys_dict = utils.test_args_sys(num_threads, delete_temps, verbose, output_as_dict=True)

    # Geometry dependent settings
    if geometry == 'parallel':
        dist_source_detector = 0.0
        magnification = 1.0
    elif geometry=='fan-curved' or geometry=='fan-flat':
        if dist_source_detector is None or magnification is None:
            raise Exception('For fan beam geometries, need to specify dist_source_detector and magnification')
    else:
        raise Exception('Unrecognized geometry {}'.format(geometry))

    geom_dict['geometry'] = geometry
    geom_dict['dist_source_detector'] = dist_source_detector
    geom_dict['magnification'] = magnification

    # Set automatic value of max_resolutions
    if max_resolutions is None :
        max_resolutions = auto_max_resolutions(init_image)
        recon_dict['max_resolutions'] = max_resolutions

    # Set automatic values of num_rows, num_cols, and roi_radius
    if delta_pixel is None:
        delta_pixel = delta_channel/magnification
        geom_dict['delta_pixel'] = delta_pixel
    if num_rows is None:
        num_rows,_ = auto_img_size(num_channels, delta_channel, delta_pixel, magnification)
        geom_dict['num_rows'] = num_rows
    if num_cols is None:
        _,num_cols = auto_img_size(num_channels, delta_channel, delta_pixel, magnification)
        geom_dict['num_cols'] = num_cols
    if roi_radius is None:
        roi_radius = auto_roi_radius(delta_pixel, num_rows, num_cols)
        geom_dict['roi_radius'] = roi_radius

    # Set automatic values for weights
    if weights is None:
        weights = calc_weights(sino, weight_type)
        inits_dict['weights'] = weights

    # Set automatic value of sigma_y
    if sigma_y is None:
        sigma_y = auto_sigma_y(sino, weights, magnification, delta_channel=delta_channel,
                                             delta_pixel=delta_pixel, snr_db=snr_db)
        noise_dict['sigma_y'] = sigma_y

    # Set automatic value of sigma_x
    # if qGGMRF mode, then set sigma_x either using the provided value by user, or with auto_sigma_x
    if prox_image is None:
        if sigma_x is None:
            sigma_x = auto_sigma_x(sino, magnification, delta_channel, sharpness)
    # if proximal map mode, then overwrite sigma_x with sigma_p
    else:
        if sigma_p is None:
            sigma_p = auto_sigma_p(sino, magnification, delta_channel, sharpness)
        sigma_x = sigma_p
    noise_dict['sigma_x'] = sigma_x
    noise_dict.pop('sigma_p')

    # Reduce num_threads for positivity=False if problems size calls for it
    # num_threads_max = max_threads(num_threads, num_slices, num_rows, num_cols, positivity=positivity)
    # if num_threads_max < num_threads:
    #    num_threads = num_threads_max
    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    # Collect the individual dicts for multires_recon and to return output parameters
    if output_params_dict is None:
        output_params_dict = dict()

    all_dicts = [geom_dict, recon_dict, inits_dict, noise_dict, qggmrf_dict, sys_dict]
    for d in all_dicts:
        output_params_dict.update(d)
    output_params_dict['sino'] = sino
    output_params_dict['angles'] = angles
    output_params_dict['svmbir_lib_path'] = svmbir_lib_path
    output_params_dict['object_name'] = object_name

    reconstruction = ci.multires_recon(**output_params_dict)

    return reconstruction



def project(image, angles, num_channels,
            geometry = 'parallel', dist_source_detector = None, magnification = None,
            delta_channel = 1.0, delta_pixel = None, center_offset = 0.0, roi_radius = None,
            num_threads = None, svmbir_lib_path = __svmbir_lib_path, delete_temps = True,
            object_name = 'object', verbose = 1):
    """project(image, angles, num_channels, geometry = 'parallel', **kwargs)

    Compute 3D forward-projection.

    Args:
        image (ndarray):
            3D numpy array of image being projected.
            The image shape is (num_slices,num_rows,num_cols). The output will contain 'num_slices' projections.
            Note the image is considered 0 outside the 'roi_radius' (disregarded pixels).
        angles (ndarray):
            1D numpy array of view angles in radians.
            'angles[k]' is the angle in radians for view :math:`k`.
        num_channels (int):
            Number of sinogram channels.
        geometry (string):
            [Default='parallel'] Scanner geometry: 'parallel', 'fan-curved', or 'fan-flat'. Note for fan geometries
            the ``dist_source_detector`` and ``magnification`` arguments must be specified.
        dist_source_detector (float):
            (Required for fan beam geometries only) Distance from X-ray focal spot to detectors, in :math:`ALU`.
        magnification (float):
            (Required for fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional): [Default=1.0] Scalar value of detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional): Scalar value of the spacing between image pixels in the 2D slice
            plane in :math:`ALU`. Defaults to ``delta_channel`` for ``parallel`` beam geometry,
            and ``delta_channel``/``magnification`` for fan beam geometries.
        center_offset (float, optional):
            [Default=0.0] Offset from center-of-rotation in 'fractional number of channels' units.
        roi_radius (float, optional): [Default=None] Radius of relevant image region in :math:`ALU`.
            Pixels outside the radius are disregarded in the forward projection.
            If not given, the value is set with auto_roi_radius().
        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system.
        svmbir_lib_path (string, optional):
            [Default='~/.cache/svmbir'] Path to directory containing library of projection matrices and temp files.
        delete_temps (bool, optional):
            [Default=True] Delete any temporary files generated during computation. Unused for cython version.
        object_name (string, optional):
            [Default='object'] Specifies base filename of temporary files. Unused for cython version.
        verbose (int, optional): [Default=1] Level of printed status output. {0,1,2} Set to 0 for quiet mode.

    Returns:
        ndarray: 3D numpy array containing projection with shape (num_views, num_slices, num_channels).
    """

    # Temporary check for argument order. From v0.2.4, order is project(image,angles,...)
    if isinstance(image,np.ndarray) and isinstance(angles,np.ndarray) and (image.ndim < angles.ndim):
        print("WARNING: Check the argument order svmbir.project(image,angles,...)")
        print("**This is the order definition as of svmbir v0.2.4")
        print("**Swapping and proceeding...")
        temp_id = image
        image = angles
        angles = temp_id

    # validate input arguments
    image = utils.test_args_image(image)
    angles = utils.test_args_angles(angles)

    if num_threads is None :
        num_threads = cpu_count(logical=False)

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    num_slices = image.shape[0]
    num_rows = image.shape[1]
    num_cols = image.shape[2]
    num_views = len(angles)

    # Issue warning that 'fan' geometry will be removed in the future (last valid version is v0.2.9)
    if geometry=='fan':
        geometry = 'fan-curved'
        warnings.warn("'fan' geometry will be removed in a future release. Fan beam geometry is now specified as either 'fan-curved' or 'fan-flat'. Defaulting to 'fan-curved'.",FutureWarning)

    # Geometry dependent settings
    if geometry == 'parallel':
        dist_source_detector = 0.0
        magnification = 1.0
    elif geometry=='fan-curved' or geometry=='fan-flat':
        if dist_source_detector is None or magnification is None:
            raise Exception('For fan beam geometries, need to specify dist_source_detector and magnification')
    else:
        raise Exception('Unrecognized geometry {}'.format(geometry))

    if delta_pixel is None:
        delta_pixel = delta_channel/magnification
    if roi_radius is None :
        roi_radius = auto_roi_radius(delta_pixel, num_rows, num_cols)

    paths, sinoparams, imgparams = ci._init_geometry(angles, center_offset=center_offset,
                                                     geometry=geometry, dist_source_detector=dist_source_detector,
                                                     magnification=magnification,
                                                     num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                     num_rows=num_rows, num_cols=num_cols,
                                                     delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                     roi_radius=roi_radius,
                                                     svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                     verbose=verbose)

    # Collect settings to pass to C
    settings = dict()
    settings['paths'] = paths
    settings['imgparams'] = imgparams
    settings['sinoparams'] = sinoparams
    settings['verbose'] = verbose
    settings['num_threads'] = num_threads
    settings['delete_temps'] = delete_temps

    # Do the projection
    proj = ci.project(image, settings)

    return proj


def backproject(sino, angles, num_rows=None, num_cols=None,
            geometry = 'parallel', dist_source_detector = None, magnification = None,
            delta_channel = 1.0, delta_pixel = None, center_offset = 0.0, roi_radius = None,
            num_threads = None, svmbir_lib_path = __svmbir_lib_path, delete_temps = True,
            object_name = 'object', verbose = 1):
    """backproject(sino, angles, **kwargs)

    Compute 3D back-projection.

    Args:
        sino (ndarray):
            3D numpy array of input sinogram with shape (num_views,num_slices,num_channels).
        angles (ndarray):
            1D numpy array of view angles in radians.
            'angles[k]' is the angle in radians for view :math:`k`.
        num_rows (int, optional):
            [Default=num_channels] Integer number of output image rows.
        num_cols (int, optional):
            [Default=num_channels] Integer number of output image columns.
        geometry (string):
            [Default='parallel'] Scanner geometry: 'parallel', 'fan-curved', or 'fan-flat'. Note for fan geometries
            the ``dist_source_detector`` and ``magnification`` arguments must be specified.
        dist_source_detector (float):
            (Required for fan beam geometries only) Distance from X-ray focal spot to detectors, in :math:`ALU`.
        magnification (float):
            (Required for fan beam geometries only) Magnification factor = dist_source_detector/dist_source_isocenter.
        delta_channel (float, optional):
            [Default=1.0] Detector channel spacing in :math:`ALU`.
        delta_pixel (float, optional): Scalar value of the spacing between image pixels in the 2D slice
            plane in :math:`ALU`. Defaults to ``delta_channel`` for ``parallel`` beam geometry,
            and ``delta_channel``/``magnification`` for fan beam geometries.
        center_offset (float, optional):
            [Default=0.0] Offset from center-of-rotation in 'fractional number of channels' units.
        roi_radius (float, optional): [Default=None] Radius of relevant image region in :math:`ALU`.
            Pixels outside the radius are disregarded in the forward projection.
            If not given, the value is set with auto_roi_radius().
        num_threads (int, optional): [Default=None] Number of compute threads requested when executed.
            If None, num_threads is set to the number of cores in the system.
        svmbir_lib_path (string, optional):
            [Default='~/.cache/svmbir'] Path to directory containing library of projection matrices and temp files.
        delete_temps (bool, optional):
            [Default=True] Delete any temporary files generated during computation. Unused for cython version.
        object_name (string, optional):
            [Default='object'] Specifies base filename of temporary files. Unused for cython version.
        verbose (int, optional): [Default=1] Level of printed status output. {0,1,2} Set to 0 for quiet mode.

    Returns:
        ndarray: 3D numpy array containing back projected image (num_slices,num_rows,num_cols).
    """

    # validate input arguments
    angles = utils.test_args_angles(angles)
    sino = utils.test_args_sino(sino, angles)

    if num_threads is None :
        num_threads = cpu_count(logical=False)

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    num_views = sino.shape[0]
    num_slices = sino.shape[1]
    num_channels = sino.shape[2]

    if num_views != len(angles):
        raise Exception('svmbir.backproject(): angles and sinogram arrays have conflicting sizes')

    # Issue warning that 'fan' geometry will be removed in the future (last valid version is v0.2.9)
    if geometry=='fan':
        geometry = 'fan-curved'
        warnings.warn("'fan' geometry will be removed in a future release. Fan beam geometry is now specified as either 'fan-curved' or 'fan-flat'. Defaulting to 'fan-curved'.",FutureWarning)

    # Geometry dependent settings
    if geometry == 'parallel':
        dist_source_detector = 0.0
        magnification = 1.0
    elif geometry=='fan-curved' or geometry=='fan-flat':
        if dist_source_detector is None or magnification is None:
            raise Exception('For fan beam geometries, need to specify dist_source_detector and magnification')
    else:
        raise Exception('Unrecognized geometry {}'.format(geometry))

    if delta_pixel is None:
        delta_pixel = delta_channel/magnification
    if num_rows is None:
        num_rows,_ = auto_img_size(num_channels, delta_channel, delta_pixel, magnification)
    if num_cols is None:
        _,num_cols = auto_img_size(num_channels, delta_channel, delta_pixel, magnification)
    if roi_radius is None:
        roi_radius = auto_roi_radius(delta_pixel, num_rows, num_cols)

    paths, sinoparams, imgparams = ci._init_geometry(angles, center_offset=center_offset,
                                                     geometry=geometry, dist_source_detector=dist_source_detector,
                                                     magnification=magnification,
                                                     num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                     num_rows=num_rows, num_cols=num_cols,
                                                     delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                     roi_radius=roi_radius,
                                                     svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                     verbose=verbose)

    # Collect settings to pass to C
    settings = dict()
    settings['paths'] = paths
    settings['imgparams'] = imgparams
    settings['sinoparams'] = sinoparams
    settings['verbose'] = verbose
    settings['num_threads'] = num_threads
    settings['delete_temps'] = delete_temps

    return ci.backproject(sino, settings)


def _sino_indicator(sino):
    """Compute a binary function that indicates the region of sinogram support.

    Args:
        sino (ndarray):
            3D numpy array of sinogram data with shape (num_views,num_slices,num_channels).

    Returns:
        int8: A binary value: =1 within sinogram support; =0 outside sinogram support.
    """
    indicator = np.int8(sino > 0.05 * np.mean(np.fabs(sino)))  # for excluding empty space from average
    return indicator
