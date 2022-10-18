import os
import numpy as np
from demo_utils import plot_image
import svmbir

"""
This file demonstrates the generation of a Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
This version allows shows the use of the 'sharpness' parameter and the ability to use the parameters returned from recon.
"""

# Simulated image parameters
num_rows_cols = 256 # assumes a square image

# Simulated sinogram parameters
num_views = 144
tilt_angle = np.pi/2 # Tilt range of +-90deg

# Reconstruction parameters
snr_db = 30.0
sharpness_values = [-1.0, 0.0, 1.0, 2.0]
T = 0.1
p = 1.2

# Multi-resolution works much better for limited and sparse view reconstruction
max_resolutions = 2  # Use 2 additional resolutions to do reconstruction

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

np.save('output/shepp_logan_2D_sino.npy', sino)
np.save('output/shepp_logan_2D_angles.npy', angles)

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform MBIR reconstruction and get the resulting parameters
# After the call to recon, params_dict will contain all of the parameters used for recon, including any defaults
# and calculated values.
params_dict = dict()
recon = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness_values[0], snr_db=snr_db, max_resolutions=max_resolutions,
                     output_params_dict=params_dict)

recon_list = [recon]
nrmse_list = [svmbir.phantom.nrmse(recon[0], phantom[0])]

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
plot_image(phantom[0], title='Shepp Logan Phantom', filename='output/shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display sinogram
plot_image(np.squeeze(sino), title='Sinogram', filename='output/shepp_logan_sinogram.png')

# Loop over other sharpness values
params_dict.pop('sigma_x')  # In order for sharpness to be used, sigma_x must be None
for j, cur_sharpness in enumerate(sharpness_values[1:]):
    params_dict['sharpness'] = cur_sharpness
    # Note that params_dict is not updated by the following call to recon since it is not passed in as
    # output_params_dict.  For instance, sigma_x gets set within recon based on sharpness, but sigma_x remains
    # unset in params_dict after the following call to recon.  To set the parameters from this call using this same
    # dict would require svmbir.recon(**params_dict, output_params_dict=params_dict)
    recon_list += [svmbir.recon(**params_dict)]
    nrmse_list += [svmbir.phantom.nrmse(recon_list[j+1][0], phantom[0])]

# display reconstructions
for j, sharpness in enumerate(sharpness_values):
    title = f'Reconstruction with sharpness={sharpness_values[j]:.1f}: NRMSE={nrmse_list[j]:.3f}.'
    plot_image(recon_list[j][0], title=title, filename='output/shepp_logan_recon.png', vmin=vmin, vmax=vmax)

input("press Enter")
