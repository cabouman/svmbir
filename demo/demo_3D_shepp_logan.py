import os
import numpy as np
from demo_utils import plot_image
import svmbir

"""
This file demonstrates the generation of a 3D Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
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
snr_db = 40.0
sharpness = 0.0
T = 0.1
p = 1.2

# Display parameters
vmin = 1.0
vmax = 1.2

# Generate phantom
phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows_cols,num_rows_cols,num_slices)

# Generate the array of view angles
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Generate sinogram by projecting phantom
sino = svmbir.project(phantom, angles, num_rows_cols )

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform fixed resolution MBIR reconstruction
recon = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db)

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon, phantom)

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/3d_shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction
title = f'Slice {display_slice:d} of 3D Recon with NRMSE={nrmse:.3f}.'
plot_image(recon[display_slice], title=title, filename='output/3d_shepp_logan_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
