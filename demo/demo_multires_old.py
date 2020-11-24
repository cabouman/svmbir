import os
import numpy as np
from svmbir.phantom import plot_image
from skimage.transform import resize
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
tilt_angle = np.pi/3 # Tilt range of +-60deg

# Reconstruction parameters
sharpness = 2.0
T = 0.25
snr_db = 30.0
p = 1.2
max_iterations = 500

# Resolution parameters
lr_delta_pixel = 2.0 # If you set this to 2.0, it works. But for 4.0, it crashes
lr_num_rows = int(num_rows/lr_delta_pixel)
lr_num_cols = int(num_cols/lr_delta_pixel)

print(f'num_rows and num_cols = ({num_rows},{num_cols})')

# Display parameters
vmin = 0.0
vmax = 1.1

# Generate phantom
phantom = svmbir.phantom.gen_microscopy_sample_3d(num_rows,num_cols,num_slices)

# Generate array of view angles form -180 to 180 degs
angles = np.linspace(-tilt_angle, tilt_angle, num_views)

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform low res MBIR reconstruction
lr_recon = svmbir.recon(sino, angles, num_rows=lr_num_rows, num_cols=lr_num_cols, T=T, p=p, sharpness=sharpness, snr_db=snr_db, delta_pixel=lr_delta_pixel, max_iterations=max_iterations )

# Interpolate resolution of reconstruction
init_image = svmbir.recon_resize(lr_recon, (num_rows, num_cols) )

# Perform full res MBIR reconstruction
recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, T=T, init_image=init_image, p=p, sharpness=sharpness, snr_db=snr_db, max_iterations=max_iterations )

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
plot_image(phantom[display_slice], title='Shepp Logan Phantom', filename='output/multires_phantom.png', vmin=vmin, vmax=vmax)

# display low res reconstruction
title = f'Slice {display_slice:d} of Low Reconstruction.'
plot_image(lr_recon[display_slice], title=title, filename='output/multires_recon.png', vmin=vmin, vmax=vmax)

# display initial image
plot_image(init_image[display_slice], title='Initial Image', filename='output/multires_init_image.png', vmin=vmin, vmax=vmax)

# display full res reconstruction
title = f'Slice {display_slice:d} of Full Reconstruction.'
plot_image(recon[display_slice], title=title, filename='output/multires_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
