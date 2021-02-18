import os
import sys
from glob import glob
import numpy as np
import pdb
import warnings
import hashlib
# pdb.set_trace()


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

    # Convert parameter ints to floats
    if isinstance(center_offset,int):
        center_offset = float(center_offset)
    if isinstance(delta_channel,int):
        delta_channel = float(delta_channel)
    if isinstance(delta_pixel,int):
        delta_pixel = float(delta_pixel)

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

    # Convert parameter ints to floats
    if isinstance(roi_radius,int):
        roi_radius = float(roi_radius)

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

    # Convert parameter ints to floats
    if isinstance(sigma_y,int):
        sigma_y = float(sigma_y)
    if isinstance(snr_db,int):
        snr_db = float(snr_db)

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

    # Convert parameter ints to floats
    if isinstance(sharpness,int):
        sharpness = float(sharpness)
    if isinstance(sigma_x,int):
        sigma_x = float(sigma_x)

    if not isinstance(sharpness, float):
        warnings.warn("Parameter sharpness is not valid float; Setting sharpness = 0.0.")
        sharpness = 0.0

    if not isinstance(positivity, bool):
        warnings.warn("Parameter positivity is not valid boolean; Setting positivity = True.")
        positivity = True

    if not ((sigma_x is None) or (isinstance(sigma_x, float) and (sigma_x > 0))):
        warnings.warn("Parameter sigma_x is not valid float; Setting sigma_x = None.")
        sigma_x = None

    return sharpness, positivity, sigma_x


def test_pqtb_values(p, q, T, b_interslice):
    """ Tests that p, q have valid values; prints warnings if necessary; and returns valid values.
    """

    # Convert parameter ints to floats
    if isinstance(p,int):
        p = float(p)
    if isinstance(q,int):
        q = float(q)
    if isinstance(T,int):
        T = float(T)
    if isinstance(b_interslice,int):
        b_interslice = float(b_interslice)

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

    if isinstance(stop_threshold,int):
        stop_threshold = float(stop_threshold)
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


def hash_params(angles, **kwargs):
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


def get_params_dicts(angles, num_channels, num_views, num_slices, num_rows, num_cols,
                    delta_channel, delta_pixel, roi_radius, center_offset, verbose,
                    svmbir_lib_path, object_name, interface = 'Cython'):
    # Collect the information needed to pass to c
    # - ideally these should be put in a struct that could be used by c directly
    # First the sinogram parameters
    sinoparams = dict()
    if interface == 'Command Line':
        sinoparams['geometry'] = '3DPARALLEL'
    sinoparams['num_channels'] = num_channels
    sinoparams['num_views'] = num_views
    sinoparams['num_slices'] = num_slices
    sinoparams['delta_channel'] = delta_channel
    sinoparams['center_offset'] = center_offset
    sinoparams['delta_slice'] = 1
    if interface == 'Command Line':
        sinoparams['first_slice_number'] = 0
        sinoparams['view_angle_list'] = object_name + '.ViewAngleList'
    else:
        sinoparams['view_angle_list'] = angles.astype(np.single)

    # Then the image parameters
    imgparams = dict()
    imgparams['Nx'] = num_cols
    imgparams['Ny'] = num_rows
    imgparams['Nz'] = num_slices
    if interface == 'Command Line':
        imgparams['first_slice_number'] = 0
    imgparams['delta_xy'] = delta_pixel
    imgparams['delta_z'] = 1
    imgparams['roi_radius'] = roi_radius

    # Collect any info needed for c subroutine
    settings = dict()
    settings['verbose'] = verbose
    settings['svmbir_lib_path'] = svmbir_lib_path
    settings['object_name'] = object_name

    return sinoparams, imgparams, settings