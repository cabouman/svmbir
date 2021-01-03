import os
import numpy as np
from svmbir.cysvmbir import *


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

    # Set image parameters
    py_imageparams = dict()
    py_imageparams['Nx'] = 128
    py_imageparams['Ny'] = 128
    py_imageparams['Deltaxy'] = 1.0
    py_imageparams['ROIRadius'] = np.float(
        py_imageparams['Deltaxy'] * max(py_imageparams['Ny'], py_imageparams['Nx'])) / 2.0
    py_imageparams['DeltaZ'] = 1.0
    py_imageparams['Nz'] = 80
    py_imageparams['FirstSliceNumber'] = 0
    py_imageparams['NumSliceDigits'] = 5

    # Set sinogram parameters
    py_sinoparams = dict()
    py_sinoparams['NChannels'] = 128
    py_sinoparams['DeltaChannel'] = 1.0
    py_sinoparams['CenterOffset'] = 0.0
    py_sinoparams['NViews'] = 32
    py_sinoparams['ViewAngles'] = np.linspace(0, np.pi, py_sinoparams['NViews']).astype(np.single)
    py_sinoparams['NSlices'] = 80
    py_sinoparams['DeltaSlice'] = 1.0
    py_sinoparams['FirstSliceNumber'] = 0
    py_sinoparams['NumSliceDigits'] = 5

    # Convert python string to bytearray. bytearray can be accepted by c function as char*.
    temp_path = "./output/tmp"
    Amatrix_fname = string_to_char_array(temp_path)

    # Compute A matrix
    cy_AmatrixComputeToFile(py_imageparams, py_sinoparams, Amatrix_fname, 2)
