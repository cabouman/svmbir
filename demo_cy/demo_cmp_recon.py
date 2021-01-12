import os
import numpy as np
import svmbir
from svmbir.cysvmbir import *
import svmbir.py_c_interface as pci
from svmbir.phantom import plot_image

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


if __name__ == '__main__':
    # create output folder
    os.makedirs('output', exist_ok=True)

    tilt_angle = np.pi / 2  # Tilt range of +-90deg
    snr_db = 30
    # Set image parameters
    py_imageparams = dict()
    py_imageparams['Nx'] = 256
    py_imageparams['Ny'] = 256
    py_imageparams['Deltaxy'] = 1.0
    py_imageparams['ROIRadius'] = np.float(
        py_imageparams['Deltaxy'] * max(py_imageparams['Ny'], py_imageparams['Nx'])) / 2.0
    py_imageparams['DeltaZ'] = 1.0
    py_imageparams['Nz'] = 33
    py_imageparams['FirstSliceNumber'] = 0
    py_imageparams['NumSliceDigits'] = 5

    # Set sinogram parameters
    py_sinoparams = dict()
    py_sinoparams['NChannels'] = 256
    py_sinoparams['DeltaChannel'] = 1.0
    py_sinoparams['CenterOffset'] = 0.0
    py_sinoparams['NViews'] = 144
    py_sinoparams['ViewAngles'] = np.linspace(-tilt_angle, tilt_angle, py_sinoparams['NViews'], endpoint=False).astype(np.single)
    py_sinoparams['NSlices'] = 33
    py_sinoparams['DeltaSlice'] = 1.0
    py_sinoparams['FirstSliceNumber'] = 0
    py_sinoparams['NumSliceDigits'] = 5


    # Convert python string to bytearray. bytearray can be accepted by c function as char*.
    temp_path = "./output/tmp"
    Amatrix_fname = string_to_char_array(temp_path)

    # Simulated image parameters
    num_rows_cols = py_imageparams['Nx']  # Assumes a square image
    num_slices = py_sinoparams['NSlices']

    # Simulated sinogram parameters
    num_views = py_sinoparams['NViews']
    display_slice = 12  # Display slice at z=-0.25

    # Generate phantom
    phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows_cols, num_rows_cols, num_slices)
    phantom = np.ascontiguousarray(phantom,dtype = np.single)

    # Titles for display images
    title_proj = f'Slice {display_slice:d} of 3D Projection.'
    title_recon = f'Slice {display_slice:d} of 3D Recon.'
    title_weight = f'Slice {display_slice:d} of 3D Projection.'
    # Compute A matrix
    cy_AmatrixComputeToFile(py_imageparams, py_sinoparams, Amatrix_fname, 2)

    # Forward project
    proj_cy = cy_forwardProject(phantom, py_imageparams, py_sinoparams, Amatrix_fname, 2)

    # display sinogram
    plot_image(proj_cy[display_slice], title=title_proj, filename='output/3d_proj_cy.png')

    weight_py = svmbir.calc_weights(np.swapaxes(proj_cy,0,1), 'unweighted')
    weight_cy = np.swapaxes(weight_py,0,1)
    weight_cy = np.ascontiguousarray(weight_cy, dtype=np.single)
    plot_image(weight_cy[display_slice], title=title_weight, filename='output/3d_weight_cy.png')
    proj_init_cy = np.zeros(np.shape(proj_cy), dtype=np.single)
    proximalmap_cy = np.zeros((num_slices, num_rows_cols, num_rows_cols), dtype=np.single)

    sharpness = 1.0
    snr_db =40.0
    # Set reconstruction parameters
    py_reconparams = dict()
    py_reconparams['ReconType'] = 1
    py_reconparams['InitImageValue'] = 0.0
    py_reconparams['StopThreshold']  = 0.001
    py_reconparams['MaxIterations'] = 100
    py_reconparams['Positivity']  = 1
    py_reconparams['SigmaY'] = svmbir.auto_sigma_y(np.swapaxes(proj_cy,0,1), weight_py, snr_db = snr_db)
    print(py_reconparams['SigmaY'])
    py_reconparams['weightType'] = 1
    py_reconparams['b_nearest']  = 1.0
    py_reconparams['b_diag'] = 0.707
    py_reconparams['b_interslice'] = 1.0
    py_reconparams['p'] = 1.1
    py_reconparams['q'] = 2.0
    py_reconparams['T'] = 0.1

    py_reconparams['SigmaX'] = svmbir.auto_sigma_x(np.swapaxes(proj_cy,0,1), sharpness = sharpness)
    print(py_reconparams['SigmaX'])
    py_reconparams['pow_sigmaX_p'] = np.power(py_reconparams['SigmaX'],py_reconparams['p'])
    py_reconparams['pow_sigmaX_q'] = np.power(py_reconparams['SigmaX'],py_reconparams['q'])
    py_reconparams['pow_T_qmp'] = np.power(py_reconparams['T'], py_reconparams['q'] - py_reconparams['p'])
    py_reconparams['SigmaXsq'] = py_reconparams['SigmaX']**2


    # Display parameters
    vmin = 1.0
    vmax = 1.2
    image_py = cy_MBIRReconstruct(proj_cy,
                       weight_cy,
                       py_imageparams,
                       py_sinoparams,
                       py_reconparams,
                       Amatrix_fname,
                       2)

    # display image
    plot_image(image_py[display_slice], title=title_recon, filename='output/3d_recon_cy.png',vmin=vmin, vmax=vmax)

    # Perform fixed resolution MBIR reconstruction
    recon = svmbir.recon(np.swapaxes(proj_cy,0,1),
                         py_sinoparams['ViewAngles'],
                         center_offset = py_sinoparams['CenterOffset'],
                         delta_channel = py_sinoparams['DeltaChannel'],
                         delta_pixel = py_imageparams['Deltaxy'],
                         num_rows = py_imageparams['Ny'],
                         num_cols = py_imageparams['Nx'],
                         roi_radius = py_imageparams['ROIRadius'],
                         sigma_y = py_reconparams['SigmaY'],
                         snr_db = snr_db,
                         weight_type = 'unweighted',
                         sharpness = sharpness,
                         positivity=py_reconparams['Positivity'],
                         sigma_x = py_reconparams['SigmaX'],
                         T = py_reconparams['T'],
                         p = py_reconparams['p'],
                         q = py_reconparams['q'],
                         b_interslice = py_reconparams['b_interslice'],
                         stop_threshold = py_reconparams['StopThreshold'],
                         max_iterations = py_reconparams['MaxIterations'],
                         max_resolutions= 0,
                         verbose =2,
                         num_threads=1.0)
    # display sinogram
    plot_image(recon[display_slice], title=title_recon, filename='output/3d_recon_py.png',vmin=vmin, vmax=vmax)

    # Compute Normalized Root Mean Squared Error
    nrmse = svmbir.phantom.nrmse(image_py, recon)
    print("svmbir error: %f" % svmbir.phantom.nrmse(recon, phantom))
    print("cython error: %f" % svmbir.phantom.nrmse(image_py, phantom))
    print("RMSE between svmbir and cython: %f" % svmbir.phantom.nrmse(image_py, recon))