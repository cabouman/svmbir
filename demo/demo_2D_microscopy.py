import numpy as np
import matplotlib.pyplot as plt
import svmbir

"""
This file demonstrates the generation of a 2D microscopy phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""

def plot_result(img, title=None, filename=None, vmin=None, vmax=None):
    """
    Function to display and save a 2D array as an image.
    :param img: 2D numpy array to display
    :param vmin: Value mapped to black
    :param vmax: Value mapped to white
    """

    plt.ion()
    fig = plt.figure()
    imgplot = plt.imshow(img, vmin=vmin, vmax=vmax)
    plt.title(label=title)
    imgplot.set_cmap('gray')
    plt.colorbar()
    plt.savefig(filename)


# Simulated image parameters
num_rows = 256
num_cols = 64

# Simulated sinogram parameters
num_views = 64
tilt_angle = np.pi/3 # Tilt range of +-30deg

# Reconstruction parameters
T = 1
p = 1.2
sharpness = 4.0
snr_db = 30.0
max_iterations = 500

# Display parameters
vmin = 0.0
vmax = 1.1

# Generate phantom with a single slice
phantom = svmbir.phantom.gen_microscopy_sample(num_rows,num_cols)
phantom = np.expand_dims(phantom, axis=0)

# Generate array of view angles form -180 to 180 degs
angles = np.linspace(-tilt_angle, tilt_angle, num_views)

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform MBIR reconstruction
recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, T=T, p=p, sharpness=sharpness, snr_db=snr_db, max_iterations=max_iterations )

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

# display phantom
plot_result(phantom[0], title='Shepp Logan Phantom', filename='output/2D_microscopy_phantom.png', vmin=vmin, vmax=vmax)

# display sinogram
plot_result(np.squeeze(sino), title='Sinogram', filename='output/2D_microscopy_sinogram.png')

# display reconstruction
title = f'Reconstruction with NRMSE={nrmse:.3f}.'
plot_result(recon[0], title=title, filename='output/2D_microscopy_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")