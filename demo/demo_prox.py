import os
import numpy as np
from svmbir.phantom import plot_image
import svmbir

"""
This file demonstrates the use of the proximal map function in svmbir. 
The phantom, sinogram, and reconstruction are then displayed. 
"""


# Simulated image parameters
num_rows_cols = 256 # Assumes a square image
num_slices = 33
display_slice = 12 # Display slice at z=-0.25

# Simulated sinogram parameters
num_views = 144
tilt_angle = np.pi/2 # Tilt range of +-90deg

# Reconstruction parameters
sigma_x = 0.2
snr_db = 40.0

# Display parameters
vmin = None
vmax = None

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

# Perform fixed resolution MBIR reconstruction using proximal map input
recon = svmbir.recon(sino, angles, init_image=phantom_rot, prox_image=phantom_rot, positivity=False, sigma_x=sigma_x, snr_db=snr_db)

# Perform multi-resolution MBIR reconstruction using proximal map input
mr_recon = svmbir.multires_recon(sino, angles, init_image=phantom_rot, prox_image=phantom_rot, positivity=False, sigma_x=sigma_x, snr_db=snr_db)

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/prox_phantom.png', vmin=vmin, vmax=vmax)

title = f'Slice {display_slice:d} of Rotated Phantom.'
plot_image(phantom_rot[display_slice], title=title, filename='output/prox_rotated_phantom.png', vmin=vmin, vmax=vmax)

# display reconstruction
title = f'Slice {display_slice:d} of 3D Proximal Map Recon.'
plot_image(recon[display_slice], title=title, filename='output/prox_recon.png', vmin=vmin, vmax=vmax)

# display reconstruction
title = f'Slice {display_slice:d} of 3D Proximal Map MR Recon.'
plot_image(recon[display_slice], title=title, filename='output/prox_mr_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
