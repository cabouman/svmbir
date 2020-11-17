import numpy as np
import matplotlib.pyplot as plt
import math
import svmbir

"""
This file demonstrates the use of the proximal map function in svmbir. 
The phantom, sinogram, and reconstruction are then displayed. 
"""

def plot_image(img, title=None, filename=None, vmin=None, vmax=None):
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
num_rows_cols = 256 # Assumes a square image
num_slices = 32
display_slice = math.floor(num_slices/2)-2 # Slice used to display

# Simulated sinogram parameters
num_views = 144
tilt_angle = np.pi/2 # Tilt range of +-45deg

# Reconstruction parameters
T = 0.1
p = 1.1
sharpness = 4.0
snr_db = 40.0

# Display parameters
vmin = 1.0
vmax = 1.2

# Generate phantom with a single slice
phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows_cols,num_rows_cols,num_slices)

# Generate array of view angles form -180 to 180 degs
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, num_rows_cols )

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Rotate image to use as input to proximal map
phantom_rot = np.swapaxes(phantom, 1, 2)

# Perform MBIR reconstruction using proximal map input
recon = svmbir.recon(sino, angles, prox_image=phantom_rot, T=T, p=p, sharpness=sharpness, snr_db=snr_db)

# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/prox_phantom.png', vmin=vmin, vmax=vmax)

# display reconstruction
title = f'Slice {display_slice:d} of of 3D Proximal Map Recon.'
plot_image(recon[display_slice], title=title, filename='output/prox_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
