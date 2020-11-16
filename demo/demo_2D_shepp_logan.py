import numpy as np
import matplotlib.pyplot as plt

import svmbir

"""
This file demonstrates the generation of a Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""


def plot_result(img, filename, vmin=None, vmax=None):
    """
    Function to display and save a 2D array as an image.
    :param img: 2D numpy array to display
    :param vmin: Value mapped to black
    :param vmax: Value mapped to white
    """
    imgplot = plt.imshow(img, vmin=vmin, vmax=vmax)
    imgplot.set_cmap('gray')
    plt.colorbar()
    plt.savefig(filename)
    plt.close()


if __name__ == '__main__':

    num_rows = 256
    num_cols = num_rows
    num_views = 144
    threshold = 0.05

    # Generate phantom with a single slice
    phantom = svmbir.phantom.gen_shepp_logan(num_rows)
    phantom = np.expand_dims(phantom, axis=0)

    # Generate array of view angles form -180 to 180 degs
    angles = np.linspace(-np.pi / 2.0, np.pi / 2.0, num_views, endpoint=False)

    # Generate sinogram by projecting phantom
    sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

    # Determine resulting number of views, slices, and channels
    (num_views, num_slices, num_channels) = sino.shape

    # Perform MBIR reconstruction
    recon = svmbir.recon(sino, angles, T=1.0, sharpness=1.0, snr_db=40.0, max_iterations=40)

    nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])
    print(f'The NRMSE reconstruction error is {nrmse:.3f}.')

    # display phantom
    plot_result(phantom[0], 'output/shepp_logan_phantom.png', vmin=1.0, vmax=1.1)

    # display sinogram
    plot_result(np.squeeze(sino), 'output/shepp_logan_sinogram.png')

    # display reconstruction
    plot_result(recon[0], 'output/shepp_logan_recon.png', vmin=1.0, vmax=1.1)
