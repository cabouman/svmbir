import numpy as np
import ctypes           # Import python package required to use cython
cimport cython          # Import cython package
cimport numpy as cnp    # Import specialized cython support for numpy
import os
from ._utils import *

__svmbir_lib_path = os.path.join(os.path.expanduser('~'), '.cache', 'svmbir', 'parbeam')

__namelen_sysmatrix = 20

# Import c data structure
cdef extern from "./sv-mbirct/src/MBIRModularDefs.h":
    # 3D Sinogram Parameters
    struct SinoParams3DParallel:
        int NChannels;         # Number of channels in detector
        float DeltaChannel;    # Detector spacing (mm)
        float CenterOffset;    # Offset of center-of-rotation ...
                               # Computed from center of detector in increasing direction (no. of channels)
                               # This can be fractional though
        int NViews;            # Number of view angles
        float *ViewAngles;     # Array of NTheta view angle entries in degrees
        int NSlices;           # Number of rows (slices) stored in Sino array
        float DeltaSlice;      # Spacing along row (slice) direction (mm)
        int FirstSliceNumber;  # Row (slice) index coresponding to first row (slice) stored in Sino array
                               # This is in absolute coordinates and is used if a partial set of slices is needed
        int NumSliceDigits;    # Number of slice numbers digits used in file name

    # 3D Image parameters
    struct ImageParams3D:
        int Nx;                 # Number of columns in image
        int Ny;                 # Number of rows in image
        float Deltaxy;          # Spacing between pixels in x and y direction (mm)
        float ROIRadius;        # Radius of the reconstruction (mm)
        float DeltaZ;           # Spacing between pixels in z direction (mm) [This should be equal to DeltaSlice
        int Nz;                 # Number of rows (slices) in image
        int FirstSliceNumber;   # Detector row (slice) index cooresponding to first row (slice) stored in Image array
                                # This is in absolute coordinates and is used if a partial set of slices is needed
        int NumSliceDigits;     # Number of slice numbers digits used in file name

    # Reconstruction Parameters Data Structure
    struct ReconParams:
        char ReconType;         # 1:QGGMRF_3D, 2:PandP
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
        float SigmaX;           # q-GGMRF sigma_x parameter (mm-1)


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
    imgparams.NumSliceDigits = 4

cdef convert_py2c_SinoParams3D(SinoParams3DParallel* sinoparams,
                        py_sinoparams,
                        float[:] ViewAngles):
    sinoparams.NChannels = py_sinoparams['num_channels']
    sinoparams.DeltaChannel = py_sinoparams['delta_channel']
    sinoparams.CenterOffset = py_sinoparams['center_offset']
    sinoparams.NViews = py_sinoparams['num_views']
    sinoparams.ViewAngles = &ViewAngles[0] # Assign pointer for float array in C data structure
    sinoparams.NSlices = py_sinoparams['num_slices']
    sinoparams.DeltaSlice = py_sinoparams['delta_slice']
    sinoparams.FirstSliceNumber = 0
    sinoparams.NumSliceDigits = 4


cdef convert_py2c_ReconParams3D(ReconParams* reconparams,
                                py_reconparams):
    reconparams.ReconType = py_reconparams['prior_model']           # 1:QGGMRF_3D, 2:PandP
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
    reconparams.SigmaX = py_reconparams['sigma_x']                   # q-GGMRF sigma_x parameter (mm-1)


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
                    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
                    svmbir_lib_path = __svmbir_lib_path, object_name = 'object'):

    # Collect the information needed to pass to c
    # - ideally these should be put in a struct that could be used by c directly
    # First the sinogram parameters
    sinoparams = dict()
    sinoparams['num_channels'] = num_channels
    sinoparams['num_views'] = num_views
    sinoparams['num_slices'] = num_slices
    sinoparams['delta_channel'] = delta_channel
    sinoparams['center_offset'] = center_offset
    sinoparams['delta_slice'] = 1
    sinoparams['view_angle_list'] = angles.astype(np.single)

    # Then the image parameters
    imgparams = dict()
    imgparams['Nx'] = num_cols
    imgparams['Ny'] = num_rows
    imgparams['Nz'] = num_slices
    imgparams['delta_xy'] = delta_pixel
    imgparams['delta_z'] = 1
    imgparams['roi_radius'] = roi_radius

    # Collect any info needed for c subroutine
    settings = dict()
    settings['verbose'] = verbose
    settings['svmbir_lib_path'] = svmbir_lib_path
    settings['object_name'] = object_name

    # Declare image and sinogram Parameter structures.
    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname

    # Convert parameter python dictionaries to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, angles.astype(np.single))

    # Get info needed for c
    hash_val, relevant_params = hash_params(angles.astype(np.single), **{**sinoparams, **imgparams})
    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val[:__namelen_sysmatrix])

    # Then call cython function to get the system matrix - the output dict can be used to pass the matrix itself
    # and/or to pass path information to a file containing the matrix
    if os.path.exists(paths['sysmatrix_name'] + '.2Dsvmatrix') :
        print('Found system matrix: {}'.format(paths['sysmatrix_name'] + '.2Dsvmatrix'))
        os.utime(paths['sysmatrix_name'] + '.2Dsvmatrix')  # update file modified time
    else :
        Amatrix_fname = string_to_char_array(paths['sysmatrix_name'] + '.2Dsvmatrix')
        AmatrixComputeToFile(imgparams_c,sinoparams_c,&Amatrix_fname[0],verbose)

    return paths, sinoparams, imgparams

def project(image, sinoparams, settings):

    paths = settings['paths']
    verbose = settings['verbose']
    imageparams = settings['imgparams']

    # Get shapes of image and projection
    cdef int nslices = np.shape(image)[0]
    cdef int nrows = np.shape(image)[1]
    cdef int ncols_img = np.shape(image)[2]

    cdef int nviews = sinoparams['num_views']
    cdef int nchannels = sinoparams['num_channels']
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname

    if not image.flags["C_CONTIGUOUS"]:
        image =  np.ascontiguousarray(image, dtype=np.single)

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_image = image

    # Allocates memory, without initialization, for matrix to be passed back from C subroutine
    cdef cnp.ndarray[float, ndim=3, mode="c"] proj = np.empty((nslices, nviews, nchannels), dtype=ctypes.c_float)

    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c

    # Write parameter to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams_c, imageparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, sinoparams['view_angle_list'])

    Amatrix_fname = string_to_char_array(paths['sysmatrix_name']+ '.2Dsvmatrix')

    # Forward projection by calling C subroutine
    forwardProject(&proj[0,0,0], &cy_image[0,0,0], imgparams_c, sinoparams_c, &Amatrix_fname[0],verbose)

    # Return cython ndarray
    return np.swapaxes(proj,0,1)

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

    reconparams = dict()
    reconparams['prior_model'] = 1     # 1:QGGMRF_3D, 2:PandP
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
    reconparams['weight_type'] = 1 # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)

    paths, sinoparams, imgparams = _init_geometry(angles, center_offset=center_offset,
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
    cdef cnp.ndarray[float, ndim=3, mode="c"] py_image
    cdef cnp.ndarray[char, ndim=1, mode="c"] Amatrix_fname

    if np.isscalar(init_image) :
        init_image_value = init_image
        py_image = np.zeros((num_slices, nrows, ncols), dtype=ctypes.c_float)+init_image_value
    else :
        init_image_value = 0
        if not init_image.flags["C_CONTIGUOUS"]:
            init_image = np.ascontiguousarray(init_image, dtype=np.single)
        py_image = np.copy(init_image).astype(ctypes.c_float)
    reconparams['init_image_value'] = init_image_value

    if init_proj is not None:
        cy_proj_init = np.swapaxes(init_proj, 0, 1)
        cy_proj_init = np.ascontiguousarray(cy_proj_init, dtype=np.single)


    if prox_image is not None:
        if not prox_image.flags["C_CONTIGUOUS"]:
            prox_image = np.ascontiguousarray(prox_image, dtype=np.single)
        cy_prox_image = prox_image


    cdef ImageParams3D imgparams_c
    cdef SinoParams3DParallel sinoparams_c
    cdef ReconParams reconparams_c

    # Write parameter to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams_c, imgparams)
    convert_py2c_SinoParams3D(&sinoparams_c, sinoparams, angles.astype(np.single))
    convert_py2c_ReconParams3D(&reconparams_c, reconparams)

    Amatrix_fname = string_to_char_array(paths['sysmatrix_name']+ '.2Dsvmatrix')

    # Forward projection by calling C subroutine
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
