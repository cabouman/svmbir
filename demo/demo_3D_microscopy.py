import numpy as np
from svmbir.phantom import plot_image
import svmbir

"""
This file demonstrates the generation of a 3D microscopy phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""

# Simulated image parameters
num_rows = 256
num_cols = 64
num_slices = 33
display_slice = 16 # Display slice at z=-0.0

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
phantom = svmbir.phantom.gen_microscopy_sample_3d(num_rows,num_cols,num_slices)

# Generate array of view angles form -180 to 180 degs
angles = np.linspace(-tilt_angle, tilt_angle, num_views)

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform MBIR reconstruction
recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, T=T, p=p, sharpness=sharpness, snr_db=snr_db, max_iterations=max_iterations )

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon, phantom)

# display phantom
plot_image(phantom[display_slice], title='Shepp Logan Phantom', filename='output/3D_microscopy_phantom.png', vmin=vmin, vmax=vmax)

# display reconstruction
title = f'Slice {display_slice:d} of Reconstruction with NRMSE={nrmse:.3f}.'
plot_image(recon[display_slice], title=title, filename='output/3D_microscopy_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")