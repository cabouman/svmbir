import numpy as np
import warnings
import hashlib
from PIL import Image


##############################
## Parameter Test Functions ##
##############################

def int_to_float(arg):
    "Convert int argument to float, otherwise pass through"
    if isinstance(arg,int):
        return float(arg)
    else:
        return arg

def test_args_angles(angles):
    "Test validity of 'angles' argument"

    # allow scalar angle input, convert to ndarray
    if isinstance(angles,float) or isinstance(angles,int):
        print("Warning: 'angles' input is a scalar. Converting to numpy array w/ size 1")
        angles = np.array([angles])

    if not isinstance(angles,np.ndarray) and (angles.ndim == 1):
        raise Exception("Error: 'angles' input not a 1D numpy array")

    return angles

def test_args_sino(sino, angles):
    "Test for valid sino structure. If 2D given, convert to 3D"

    angles = test_args_angles(angles)

    if isinstance(sino,np.ndarray) and (sino.ndim in [1,2,3]) :
        if sino.ndim == 1 :
            print("Warning: Input sino array only 1D. Adding singletons for slice and angle axes.")
            sino = sino[np.newaxis, np.newaxis, :]
        if sino.ndim == 2 :
            if angles.size > 1 :
                print("Warning: Input sino array only 2D. Adding singleton for slice axis.")
                sino = sino[:, np.newaxis, :]
            else:
                print("Warning: Input sino array only 2D. Adding singleton for angle axis.")
                sino = sino[np.newaxis, :, :]
    else:
        raise Exception("Error: 'sino' input is not a 3D numpy array")

    if sino.shape[0] != angles.size :
        raise Exception("Error: Input 'sino' and 'angles' shapes don't agree")

    return sino

def test_args_image(image):
    "Test for valid image structure. If 2D given, convert to 3D"

    if isinstance(image,np.ndarray) and ((image.ndim==2) or (image.ndim==3)):
        if image.ndim == 2 :
            print("Warning: Input image array only 2D. Adding singleton for slice axis.")
            image = image[np.newaxis, :, :]
    else:
        raise Exception("Error: image input is not a 3D numpy array")

    return image


def test_args_geom(num_rows, num_cols, delta_pixel, roi_radius, delta_channel, center_offset):

    if not num_rows is None:
        if not (isinstance(num_rows, int) and num_rows>0):
            warnings.warn("Parameter num_rows not a valid int. Setting to default.")
            num_rows = None

    if not num_cols is None:
        if not (isinstance(num_cols, int) and num_cols>0):
            warnings.warn("Parameter num_cols not a valid int. Setting to default.")
            num_cols = None

    delta_pixel = int_to_float(delta_pixel)
    if not ((delta_pixel is None) or (isinstance(delta_pixel, float) and (delta_pixel > 0))):
        warnings.warn("Parameter delta_pixel is not valid float; Setting delta_pixel = 1.0.")
        delta_pixel = 1.0

    roi_radius = int_to_float(roi_radius)
    if not ((roi_radius is None) or ((isinstance(roi_radius, float) and (roi_radius > 0)))):
        warnings.warn("Parameter roi_radius is not valid. Setting to default.")
        roi_radius = None

    delta_channel = int_to_float(delta_channel)
    if not (isinstance(delta_channel, float) and delta_channel>0):
        warnings.warn("Parameter delta_channel is not valid float; Setting delta_channel = 1.0.")
        delta_channel = 1.0

    center_offset = int_to_float(center_offset)
    if not isinstance(center_offset, float):
        warnings.warn("Parameter center_offset is not valid float; Setting center_offset = 0.0.")
        center_offset = 0.0

    return num_rows, num_cols, delta_pixel, roi_radius, delta_channel, center_offset


def test_args_recon(sharpness, positivity, max_resolutions, stop_threshold, max_iterations):

    sharpness = int_to_float(sharpness)
    if not isinstance(sharpness, float):
        warnings.warn("Parameter sharpness is not valid float; Setting sharpness = 0.0.")
        sharpness = 0.0

    if not isinstance(positivity, bool):
        warnings.warn("Parameter positivity is not valid boolean; Setting positivity = True.")
        positivity = True

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

    return sharpness, positivity, max_resolutions, stop_threshold, max_iterations


def test_args_inits(init_image, prox_image, init_proj, weights, weight_type):

    init_image = int_to_float(init_image)
    if not (isinstance(init_image, float) or (isinstance(init_image, np.ndarray) and (init_image.ndim == 3))):
        warnings.warn("Parameter init_image is not a valid float or 3D ndarray. Setting init_image = 0.0.")
        init_image = 0.0

    if not ((prox_image is None) or (isinstance(prox_image, np.ndarray) and (prox_image.ndim == 3))):
        warnings.warn("Parameter prox_image is not a valid 3D ndarray. Setting prox_image = None.")
        prox_image = None

    if not ((init_proj is None) or (isinstance(init_proj, np.ndarray) and (init_proj.ndim == 3))):
        warnings.warn("Parameter init_proj is not a valid 3D ndarray; Setting init_proj = None.")
        init_proj = None

    if not ((weights is None) or (isinstance(weights, np.ndarray) or (weights.ndim == 3))):
        warnings.warn("Parameter weights is not valid 3D np array; Setting weights = None.")
        weights = None

    list_of_weights = ['unweighted', 'transmission', 'transmission_root', 'emission']
    if not (isinstance(weight_type, str) and (weight_type in list_of_weights)):
        warnings.warn("Parameter weight_type is not valid string; Setting roi_radius = 'unweighted'")
        weight_type = 'unweighted'

    return init_image, prox_image, init_proj, weights, weight_type


def test_args_noise(sigma_y, snr_db, sigma_x, sigma_p):

    sigma_y = int_to_float(sigma_y)
    if not ((sigma_y is None) or (isinstance(sigma_y, float) and (sigma_y > 0))):
        warnings.warn("Parameter sigma_y is not a valid float. Setting to default.")
        sigma_y = None

    snr_db = int_to_float(snr_db)
    if not isinstance(snr_db, float):
        warnings.warn("Parameter snr_db is not a valid float. Setting snr_db = 30.")
        snr_db = 30

    sigma_x = int_to_float(sigma_x)
    if not ((sigma_x is None) or (isinstance(sigma_x, float) and (sigma_x > 0))):
        warnings.warn("Parameter sigma_x is not a valid float. Setting to default.")
        sigma_x = None

    sigma_p = int_to_float(sigma_p)
    if not ((sigma_p is None) or (isinstance(sigma_p, float) and (sigma_p > 0))):
        warnings.warn("Parameter sigma_p is not a valid float. Setting to default.")
        sigma_p = None

    return sigma_y, snr_db, sigma_x, sigma_p


def test_args_qggmrf(p, q, T, b_interslice):

    # Check that q is valid
    q = int_to_float(q)
    if not (isinstance(q, float) and (1.0 <= q <= 2.0)):
        q = 2.0
        warnings.warn("Parameter q not in the valid range of [1,2]; Setting q = 2.0")

    # Check that p is valid
    p = int_to_float(p)
    if not (isinstance(p, float) and (1.0 <= p <= 2.0)):
        p = 1.2
        warnings.warn("Parameter p not in the valid range [1,2]; Setting p = 1.2")

    # Check that p and q are jointly valid
    if p > q:
        p = q
        warnings.warn("Parameter p > q; Setting p = q.")

    T = int_to_float(T)
    if not (isinstance(T, float) and T>0):
        T = 1.0
        warnings.warn("Parameter T is invalid; Setting T = 1.0")

    b_interslice = int_to_float(b_interslice)
    if not (isinstance(b_interslice, float) and b_interslice>0):
        b_interslice = 1.0
        warnings.warn("Parameter b_interslice is invalid; Setting b_interslice = 1.0")

    return p, q, T, b_interslice


def test_args_sys(num_threads, delete_temps, verbose):

    if not (isinstance(num_threads, int) and (num_threads > 0)):
        warnings.warn("Parameter num_threads is not a valid int. Setting to default.")
        num_threads = None

    if not isinstance(delete_temps, bool):
        warnings.warn("Parameter delete_temps is not valid. Setting delete_temps = True.")
        delete_temps = True

    if not (isinstance(verbose, int) and (verbose >= 0)):
        warnings.warn("Parameter verbose is not valid. Setting verbose = 1.")
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

def get_reconparams_dicts(sigma_y, positivity, sigma_x, p, q, T, b_interslice,
                            stop_threshold, max_iterations,init_image_value=0, interface = 'Cython'):
    reconparams = dict()
    if interface == 'Command Line':
        reconparams['prior_model'] = 'QGGMRF'
        reconparams['init_image_value'] = init_image_value
    else:
        reconparams['prior_model'] = 1
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

    if interface == 'Command Line':
        reconparams['weight_type'] = 'unweighted'  # constant weights
    else:
        reconparams['weight_type'] = 1 # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)

    return reconparams


def recon_resize(recon, output_shape):
    """Resizes a reconstruction by performing 2D resizing along the slices dimension

    Args:
        recon (ndarray): 3D numpy array containing reconstruction with shape (slices, rows, cols)
        output_shape (tuple): (num_rows, num_cols) shape of resized output

    Returns:
        ndarray: 3D numpy array containing interpolated reconstruction with shape (num_slices, num_rows, num_cols).
    """

    recon_resized = np.empty((recon.shape[0],output_shape[0],output_shape[1]), dtype=recon.dtype)
    for i in range(recon.shape[0]):
        PIL_image = Image.fromarray(recon[i])
        PIL_image_resized = PIL_image.resize((output_shape[1],output_shape[0]), resample=Image.BILINEAR)
        recon_resized[i] = np.array(PIL_image_resized)

    return recon_resized


