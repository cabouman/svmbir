# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 by SVMBIR Developers
# All rights reserved. BSD 3-clause License.

import numpy as np
import ctypes           # Import python package required to use cython
cimport cython          # Import cython package
cimport numpy as cnp    # Import specialized cython support for numpy
cimport openmp
import os
import random
import svmbir._utils as utils

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

__namelen_sysmatrix = 20

# Import c data structure
cdef extern from "./sv-mbirct/src/MBIRModularDefs.h":
    # 3D Sinogram Parameters
    struct SinoParams3DParallel:
        int Geometry;           # 0:parallel, 1:fanbeam
        int NChannels;          # Number of channels in detector
        float DeltaChannel;     # Detector spacing
        float CenterOffset;     # Offset of center-of-rotation, computed from center of detector in
                                #   increasing direction (fractional no. of channels)
        float DistSourceDetector; # (fanbeam only) Distance from source to detectors
        float Magnification;    # (fanbeam only) magnification = dist_source_detector / dist_source_isocenter
        int NViews;             # Number of view angles
        float *ViewAngles;      # Array of NTheta view angle entries in degrees
        int NSlices;            # Number of rows (slices) stored in Sino array
        float DeltaSlice;       # Spacing along row (slice) direction
        int FirstSliceNumber;   # Unused but will set to zero for clean C function summary

    # 3D Image parameters
    struct ImageParams3D:
        int Nx;                 # Number of columns in image
        int Ny;                 # Number of rows in image
        int Nz;                 # Number slices in image
        float Deltaxy;          # Spacing between pixels in x and y direction
        float DeltaZ;           # Spacing between pixels in z direction [This should be equal to DeltaSlice
        float ROIRadius;        # Radius of the reconstruction
        int FirstSliceNumber;   # Unused but will set to zero for clean C function summary

    # Reconstruction Parameters Data Structure
    struct ReconParams:
        char ReconType;         # 1:QGGMRF, 2:PandP, 3:Backproject
        # General parameters
        float InitImageValue;   # Initial Condition pixel value. In our examples usually chosen as ...
        float StopThreshold;    # Stopping threshold in percent
        int MaxIterations;      # Maximum number of iterations
        char Positivity;        # Positivity constraint: 1=yes, 0=no
        # sinogram weighting
        float SigmaY;           # Scaling constant for sinogram weights (e.g. W=exp(-y)/SigmaY^2 )
        int weightType;         # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)
        # neighbor weights
        float b_nearest;        # Relative nearest neighbor weight [default = 1]
        float b_diag;           # Relative diagonal neighbor weight in (x,y) plane [default = 1/sqrt(2)]
        float b_interslice;     # Relative neighbor weight along z direction [default = 1]
        # QGGMRF
        float p;                # q-GGMRF p parameter
        float q;                # q-GGMRF q parameter (q=2 is typical choice)
        float T;                # q-GGMRF T parameter
        float SigmaX;           # q-GGMRF sigma_x parameter

# Import a c function to compute A matrix.
cdef extern from "./sv-mbirct/src/A_comp.h":
    void AmatrixComputeToFile(
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char verboseLevel);

# Import a c function to project a 3D object to sinogram with a computed A matrix.
cdef extern from "./sv-mbirct/src/recon3d.h":
    void forwardProject(
        float *proj,
        float *image,
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char backproject_flag,
        char verboseLevel);

    void MBIRReconstruct(
        float *image,
        float *sino,
        float *weight,
        float *proj_init,
        float *proximalmap,
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        ReconParams reconparams,
        char *Amatrix_fname,
        char verboseLevel);


cdef convert_py2c_ImageParams3D(ImageParams3D* imgparams,
                                py_imageparams):
    imgparams.Nx = py_imageparams['Nx']
    imgparams.Ny = py_imageparams['Ny']
    imgparams.Deltaxy = py_imageparams['delta_xy']
    imgparams.ROIRadius = py_imageparams['roi_radius']
    imgparams.DeltaZ = py_imageparams['delta_z']
    imgparams.Nz = py_imageparams['Nz']
    imgparams.FirstSliceNumber = 0


cdef convert_py2c_SinoParams3D(SinoParams3DParallel* sinoparams,
                        py_sinoparams,
                        float[:] ViewAngles):
    if py_sinoparams['geometry']=='parallel':
        sinoparams.Geometry = 0
    elif py_sinoparams['geometry']=='fan':
        sinoparams.Geometry = 1
    else:
        sinoparams.Geometry = 0
    sinoparams.NChannels = py_sinoparams['num_channels']
    sinoparams.DeltaChannel = py_sinoparams['delta_channel']
    sinoparams.CenterOffset = py_sinoparams['center_offset']
    sinoparams.DistSourceDetector = py_sinoparams['dist_source_detector']
    sinoparams.Magnification = py_sinoparams['magnification']
    sinoparams.NViews = py_sinoparams['num_views']
    sinoparams.ViewAngles = &ViewAngles[0] # Assign pointer for float array in C data structure
    sinoparams.NSlices = py_sinoparams['num_slices']
    sinoparams.DeltaSlice = py_sinoparams['delta_slice']
    sinoparams.FirstSliceNumber = 0


cdef convert_py2c_ReconParams3D(ReconParams* reconparams,
                                py_reconparams):
    reconparams.ReconType = py_reconparams['prior_model']           # 1:QGGMRF, 2:PandP, 3:Backproject
    # General parameters
    reconparams.InitImageValue = py_reconparams['init_image_value']   # Initial Condition pixel value. In our examples usually chosen as ...
    reconparams.StopThreshold = py_reconparams['stop_threshold']     # Stopping threshold in percent
    reconparams.MaxIterations = py_reconparams['max_iterations']     # Maximum number of iterations
    reconparams.Positivity = py_reconparams['positivity']           # Positivity constraint: 1=yes, 0=no
    # sinogram weighting
    reconparams.SigmaY = py_reconparams['sigma_y']                   # Scaling constant for sinogram weights (e.g. W=exp(-y)/SigmaY^2 )
    reconparams.weightType = py_reconparams['weight_type']           # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)
    # neighbor weights
    reconparams.b_nearest = py_reconparams['b_nearest']             # Relative nearest neighbor weight [default = 1]
    reconparams.b_diag = py_reconparams['b_diag']                   # Relative diagonal neighbor weight in (x,y) plane [default = 1/sqrt(2)]
    reconparams.b_interslice = py_reconparams['b_interslice']       # Relative neighbor weight along z direction [default = 1]
    # QGGMRF
    reconparams.p = py_reconparams['p']                             # q-GGMRF p parameter
    reconparams.q = py_reconparams['q']                             # q-GGMRF q parameter (q=2 is typical choice)
    reconparams.T = py_reconparams['T']                             # q-GGMRF T parameter
    reconparams.SigmaX = py_reconparams['sigma_x']                   # q-GGMRF sigma_x parameter


def string_to_char_array(input_str):
    """
    Args:
        input_str:  python string
    Returns:
        0-terminated array of unsigned byte with ascii representation of input_str
    """
    len_str = len(input_str)  # Get the input length to prepare output space
    output_char_array = np.zeros(len_str + 1,
                          dtype=np.ubyte)  # Create output array - note the len_str+1 to give 0-terminated array
    output_char_array[:len_str] = bytearray(input_str.encode('ascii'))  # Fill in the output array with the input string

    # Thilo's better version:
    # output_char_array = bytearray((input_str+"\0").encode('ascii'))

    return output_char_array


def _gen_paths(svmbir_lib_path = __svmbir_lib_path, object_name = 'object', sysmatrix_name = 'object'):
    os.makedirs(os.path.join(svmbir_lib_path, 'sysmatrix'), exist_ok=True)

    paths = dict()
    paths['sysmatrix_name'] = os.path.join(svmbir_lib_path, 'sysmatrix', sysmatrix_name)

    return paths


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
                svmbir_lib_path, object_name, interface='Cython')

    # Declare image and sinogram Parameter structures.
    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname_tmp
    cdef cnp.ndarray[float, ndim=1, mode="c"] cy_angles = angles.astype(np.single)

    # Convert parameter python dictionaries to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, cy_angles)

    # Get info needed for c
    hash_val, relevant_params = utils.hash_params(angles.astype(np.single), **{**sinoparams, **imgparams})
    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val[:__namelen_sysmatrix])

    # Then call cython function to get the system matrix - the output dict can be used to pass the matrix itself
    # and/or to pass path information to a file containing the matrix
    Amatrix_file = paths['sysmatrix_name'] + '.2Dsvmatrix'
    if os.path.exists(Amatrix_file) :
        os.utime(Amatrix_file)  # update file modified time
        if verbose > 0:
            print('Found system matrix: {}'.format(Amatrix_file))
    # if matrix file does not exist, then write to tmp file and rename
    else :
        Amatrix_file_tmp = paths['sysmatrix_name'] + '_pid' + str(os.getpid()) + '_rndnum' + str(random.randint(0,1000)) + '.2Dsvmatrix'
        Amatrix_fname_tmp = string_to_char_array(Amatrix_file_tmp)
        AmatrixComputeToFile(imgparams_c,sinoparams_c,&Amatrix_fname_tmp[0],verbose)
        os.rename(Amatrix_file_tmp,Amatrix_file)

    return paths, sinoparams, imgparams


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
    num_threads = settings['num_threads']

    openmp.omp_set_num_threads(num_threads)

    # Get shapes of image and projection
    nslices = image.shape[0]
    nviews = sinoparams['num_views']
    nchannels = sinoparams['num_channels']

    # Ensure image memory is aligned properly
    if not image.flags["C_CONTIGUOUS"]:
        image = np.ascontiguousarray(image, dtype=np.single)
    else:
        image = image.astype(np.single, copy=False)

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_image = image
    cdef cnp.ndarray[float, ndim=1, mode="c"] cy_angles = sinoparams['view_angle_list']

    # Allocates memory, without initialization, for matrix to be passed back from C subroutine
    cdef cnp.ndarray[float, ndim=3, mode="c"] proj = np.empty((nslices, nviews, nchannels), dtype=ctypes.c_float)

    # Write parameter to c structures based on given py parameter List.
    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, cy_angles)

    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname
    Amatrix_fname = string_to_char_array(paths['sysmatrix_name']+ '.2Dsvmatrix')

    # Forward projection by calling C subroutine
    forwardProject(&proj[0,0,0], &cy_image[0,0,0], imgparams_c, sinoparams_c, &Amatrix_fname[0], 0, verbose)

    # Return cython ndarray
    return np.swapaxes(proj,0,1)


def backproject(sino, settings):
    """Back projection function used by svmbir.backproject().

    Args:
        sino (ndarray): 3D sinogram of shape (num_angles,num_slices,num_channels)
        settings (dict): Dictionary containing back projection settings

    Returns:
        ndarray: Backprojected image of shape (num_slices,num_rows,num_cols)
    """

    paths = settings['paths']
    imgparams = settings['imgparams']
    sinoparams = settings['sinoparams']
    verbose = settings['verbose']
    num_threads = settings['num_threads']

    openmp.omp_set_num_threads(num_threads)

    # Get shapes of sinogram and image
    nslices = sino.shape[1]
    nrows = imgparams['Ny']
    ncols = imgparams['Nx']

    # the C routine expects (Nslices,Nangles,Nchannels)
    sino = np.swapaxes(sino,0,1)
    if not sino.flags["C_CONTIGUOUS"]:
        sino = np.ascontiguousarray(sino, dtype=np.single)
    else:
        sino = sino.astype(np.single, copy=False)

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_sino = sino
    cdef cnp.ndarray[float, ndim=1, mode="c"] cy_angles = sinoparams['view_angle_list']

    # Allocates memory, without initialization, for matrix to be passed back from C subroutine
    cdef cnp.ndarray[float, ndim=3, mode="c"] image = np.empty((nslices,nrows,ncols), dtype=ctypes.c_float)

    # Write parameters to c structures
    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, cy_angles)

    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname
    Amatrix_fname = string_to_char_array(paths['sysmatrix_name']+ '.2Dsvmatrix')

    # Back project by calling C subroutine
    forwardProject(&cy_sino[0,0,0], &image[0,0,0], imgparams_c, sinoparams_c, &Amatrix_fname[0], 1, verbose)

    return image


def multires_recon(sino, angles, weights, weight_type, init_image, prox_image, init_proj,
                   geometry, dist_source_detector, magnification,
                   num_rows, num_cols, roi_radius, delta_channel, delta_pixel, center_offset,
                   sigma_y, snr_db, sigma_x, p, q, T, b_interslice,
                   sharpness, positivity, max_resolutions, stop_threshold, max_iterations,
                   num_threads, delete_temps, svmbir_lib_path, object_name, verbose):
    """Multi-resolution SVMBIR reconstruction used by svmbir.recon().

    Args: See svmbir.recon() for argument structure
    """

    # Declare cython image array here so we can initialize in recursion block
    cdef cnp.ndarray[float, ndim=3, mode="c"] py_image

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
                        sigma_y=lr_sigma_y, snr_db=snr_db, sigma_x=sigma_x, p=p,q=q,T=T,b_interslice=b_interslice,
                        sharpness=sharpness, positivity=positivity, max_resolutions=new_max_resolutions,
                        stop_threshold=stop_threshold, max_iterations=max_iterations, num_threads=num_threads,
                        delete_temps=delete_temps, svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                        verbose=verbose)

        # Interpolate resolution of reconstruction
        new_init_image = utils.recon_resize(lr_recon, (num_rows, num_cols))
        del lr_recon

        # Initialize cython image array and de-allocate
        if not new_init_image.flags["C_CONTIGUOUS"]:
            new_init_image = np.ascontiguousarray(new_init_image, dtype=np.single)
        else:
            new_init_image = new_init_image.astype(np.single, copy=False)
        py_image = new_init_image

    # Perform reconstruction at current resolution
    if verbose >= 1 :
        print(f'Reconstructing axial size (rows,cols)=({num_rows},{num_cols}).')

    # Collect parameters to pass to C
    (num_views, num_slices, num_channels) = sino.shape

    reconparams = utils.get_reconparams_dicts(sigma_y, positivity, sigma_x, p, q, T, b_interslice,
                        stop_threshold, max_iterations, interface = 'Cython')

    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
                                                  geometry=geometry, dist_source_detector=dist_source_detector,
                                                  magnification=magnification,
                                                  num_channels=num_channels, num_views=num_views, num_slices=num_slices,
                                                  num_rows=num_rows, num_cols=num_cols,
                                                  delta_channel=delta_channel, delta_pixel=delta_pixel,
                                                  roi_radius=roi_radius,
                                                  svmbir_lib_path=svmbir_lib_path, object_name=object_name,
                                                  verbose=verbose)
    # Collect data and settings to pass to c
    cdef int nrows = imgparams['Ny']
    cdef int ncols = imgparams['Nx']
    py_sino = np.swapaxes(sino, 0, 1)
    py_sino = np.ascontiguousarray(py_sino, dtype=np.single)
    py_weight = np.swapaxes(weights, 0, 1)/sigma_y**2
    py_weight = np.ascontiguousarray(py_weight, dtype=np.single)

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_sino = py_sino
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_weight = py_weight
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_proj_init
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_prox_image
    #cdef cnp.ndarray[float, ndim=3, mode="c"] py_image
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname

    if 'py_image' not in locals():
        if np.isscalar(init_image):
            py_image = np.zeros((num_slices, nrows, ncols), dtype=ctypes.c_float) + init_image
        else:
            if not init_image.flags["C_CONTIGUOUS"]:
                init_image = np.ascontiguousarray(init_image, dtype=np.single)
            else:
                init_image = init_image.astype(np.single, copy=False)
            py_image = init_image

    if np.isscalar(init_image):
        reconparams['init_image_value'] = init_image
    else:
        reconparams['init_image_value'] = 0

    if init_proj is not None:
        cy_proj_init = np.swapaxes(init_proj, 0, 1)
        cy_proj_init = np.ascontiguousarray(cy_proj_init, dtype=np.single)

    if prox_image is not None:
        if not prox_image.flags["C_CONTIGUOUS"]:
            prox_image = np.ascontiguousarray(prox_image, dtype=np.single)
        else:
            prox_image = prox_image.astype(np.single, copy=False)
        cy_prox_image = prox_image

    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    cdef ReconParams reconparams_c
    cdef cnp.ndarray[float, ndim=1, mode="c"] cy_angles = angles.astype(np.single)

    # Write parameter to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, cy_angles)
    convert_py2c_ReconParams3D(&reconparams_c, reconparams)

    Amatrix_fname = string_to_char_array(paths['sysmatrix_name']+ '.2Dsvmatrix')

    openmp.omp_set_num_threads(num_threads)

    # Reconstruct by calling C subroutine
    MBIRReconstruct(&py_image[0,0,0],
                    &cy_sino[0,0,0],
                    &cy_weight[0,0,0],
                    &cy_proj_init[0,0,0] if init_proj is not None else NULL,
                    &cy_prox_image[0,0,0] if prox_image is not None else NULL,
                    imgparams_c,
                    sinoparams_c,
                    reconparams_c,
                    &Amatrix_fname[0],
                    verbose)

    # Return cython ndarray
    return py_image
