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
    # Set image parameters
    py_imageparams = dict()
    py_imageparams['Nx'] = 256
    py_imageparams['Ny'] = 256
    py_imageparams['Deltaxy'] = 1.0
    py_imageparams['ROIRadius'] = np.float(
        py_imageparams['Deltaxy'] * max(py_imageparams['Ny'], py_imageparams['Nx'])) / 2.0
    py_imageparams['DeltaZ'] = 1.0
    py_imageparams['Nz'] = 32
    py_imageparams['FirstSliceNumber'] = 0
    py_imageparams['NumSliceDigits'] = 5

    # Set sinogram parameters
    py_sinoparams = dict()
    py_sinoparams['NChannels'] = 256
    py_sinoparams['DeltaChannel'] = 1.0
    py_sinoparams['CenterOffset'] = 0.0
    py_sinoparams['NViews'] = 144
    py_sinoparams['ViewAngles'] = np.linspace(-tilt_angle, tilt_angle, py_sinoparams['NViews']).astype(np.single)
    py_sinoparams['NSlices'] = 32
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

    # Generate sinogram by projecting phantom
    title = f'Slice {display_slice:d} of 3D Projection.'
    proj_exe = svmbir.project(py_sinoparams['ViewAngles'], phantom, num_rows_cols)
    plot_image(proj_exe[:,display_slice,:], title=title, filename='output/3d_proj_exe.png')

    # Compute A matrix
    cy_AmatrixComputeToFile(py_imageparams, py_sinoparams, Amatrix_fname, 2)

    # Forward project
    proj_cy = cy_forwardProject(phantom, py_imageparams, py_sinoparams, Amatrix_fname, 2)

    # display sinogram
    plot_image(proj_cy[display_slice], title=title, filename='output/3d_proj_cy.png')

    # Compute Normalized Root Mean Squared Error
    nrmse = svmbir.phantom.nrmse(proj_cy, np.swapaxes(proj_exe,0,1))
    print("error: %f"%nrmse)