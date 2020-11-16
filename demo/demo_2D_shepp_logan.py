import numpy as np
import matplotlib.pyplot as plt

import svmbir

"""
This file demonstrates the generation of a Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""


def plot_result(img, title=None, filename=None, vmin=None, vmax=None):
    """
    Function to display and save a 2D array as an image.
    :param img: 2D numpy array to display
    :param vmin: Value mapped to black
    :param vmax: Value mapped to white
    """

    fig = plt.figure()
    imgplot = plt.imshow(img, vmin=vmin, vmax=vmax)
    plt.title(label=title)
    imgplot.set_cmap('gray')
    plt.colorbar()
    plt.savefig(filename)
    #plt.close()


if __name__ == '__main__':

    # Simulation parameters
    num_rows = 256
    num_cols = num_rows
    num_views = 144

    # Reconstruction parameters
    T = 0.1
    p = 1.1
    sharpness = 2.0
    snr_db = 40.0

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
    recon = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db)

    # Compute Normalized Root Mean Squared Error
    nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

    # display phantom
    plot_result(phantom[0], title='Shepp Logan Phantom', filename='output/shepp_logan_phantom.png', vmin=1.0, vmax=1.1)

    # display sinogram
    plot_result(np.squeeze(sino), title='Sinogram', filename='output/shepp_logan_sinogram.png')

    # display reconstruction
    title = f'Reconstruction with NRMSE={nrmse:.3f}.'
    plot_result(recon[0], title=title, filename='output/shepp_logan_recon.png', vmin=1.0, vmax=1.1)

    plt.show()
