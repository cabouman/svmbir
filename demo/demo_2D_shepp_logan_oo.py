import os
import numpy as np
from demo_utils import plot_image
import svmbir
import svmbir.oo_svmbir as oosvmbir

"""
This file demonstrates the object-oriented interface on the generation of a Shepp-Logan phantom followed by 
sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 

The primary class is ParallelBeamCT, which has set_params, project, backproject, and recon.
"""

# #################################################################
# Set up the phantom parameters and generate the phantom
# #################################################################

# Generate the array of view angles
num_views = 144
tilt_angle = np.pi / 2  # Tilt range of +-90deg
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Simulated image parameters
num_rows_cols = 256  # assumes a square image

# Generate a 2D phantom
phantom = svmbir.phantom.gen_shepp_logan(num_rows_cols, num_rows_cols)
phantom = np.expand_dims(phantom, axis=0)

# ##########################################################################################
# Make an instance of the main class and set the geometry and reconstruction parameters
# ##########################################################################################

pbct = oosvmbir.ParallelBeamCT()

pbct.set_params(num_rows=num_rows_cols, num_cols=num_rows_cols)

# Reconstruction parameters
pbct.set_params(T=0.1, p=1.1, sharpness=0.0, snr_db=40.0)

# ##########################################################################################
# Use the instance to project the phantom to a sinogram, then do the reconstruction
# ##########################################################################################

# Generate sinogram by projecting phantom
num_channels = num_rows_cols
sino = pbct.project(phantom, angles, num_channels)

# Perform MBIR reconstruction
recon = pbct.recon(sino, angles)

# ########################################
# Calculate error and display results
# ########################################

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
vmin = 1.0
vmax = 1.2
plot_image(phantom[0], title='Shepp Logan Phantom', filename='output/shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display sinogram
plot_image(np.squeeze(sino), title='Sinogram', filename='output/shepp_logan_sinogram.png')

# display reconstruction
title = f'Reconstruction with NRMSE={nrmse:.3f}.'
plot_image(recon[0], title=title, filename='output/shepp_logan_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
