import os
import numpy as np
from demo_utils import plot_image
import svmbir

"""
This file demonstrates the generation of a Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""

# Simulated image parameters
num_rows_cols = 256 # assumes a square image

# Simulated sinogram parameters
num_views = 144
tilt_angle = np.pi/2 # Tilt range of +-90deg

# Reconstruction parameters
snr_db = 30.0
sharpness = 0.0
T = 0.1
p = 1.2

# Multi-resolution works much better for limited and sparse view reconstruction
max_resolutions=2 # Use 2 additional resolutions to do reconstruction

# Display parameters
vmin = 1.0
vmax = 1.2

# Generate phantom with a single slice
phantom = svmbir.phantom.gen_shepp_logan(num_rows_cols, num_rows_cols)
phantom = np.expand_dims(phantom, axis=0)

# Generate the array of view angles
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Generate sinogram by projecting phantom
sino = svmbir.project(phantom, angles, num_rows_cols )

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform MBIR reconstruction
recon = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db, max_resolutions = max_resolutions)

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
plot_image(phantom[0], title='Shepp Logan Phantom', filename='output/shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display sinogram
plot_image(np.squeeze(sino), title='Sinogram', filename='output/shepp_logan_sinogram.png')

# display reconstruction
title = f'Reconstruction with NRMSE={nrmse:.3f}.'
plot_image(recon[0], title=title, filename='output/shepp_logan_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
