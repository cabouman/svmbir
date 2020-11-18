import numpy as np
from skimage.restoration import denoise_nl_means, estimate_sigma
import time
from svmbir.phantom import plot_image
import svmbir

"""
This file demonstrates the denoising effect by skimage.restoration.denoise_nl_means. 
The phantom, noisy phantom, and denoised are then displayed. 
"""

# Simulated image parameters
num_rows_cols = 256 # Assumes a square image
num_slices = 32
display_slice = 13 # Display slice at z=-0.25

# Display parameters
vmin = 1.0
vmax = 1.2

# Generate 3D Shepp-Logan phantom
phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows_cols,num_rows_cols,num_slices)

# Generate noise 3D Shepp-Logan phantom
mean = 0
var = 1e-4
sigma = var ** 0.5
phantom_noisy = phantom+np.random.normal(mean,sigma,phantom.shape)

# Perform non-local means denoiser
start_time = time.time()
sigma_est = np.mean(estimate_sigma(phantom_noisy, multichannel=False))
print("Estimate sigma = %.3f"%sigma_est)

phantom_denoised= denoise_nl_means(phantom_noisy, patch_size=3, patch_distance=4, multichannel=False, fast_mode=True,sigma=sigma_est, preserve_range=True)
print("--- %s seconds ---" % (time.time() - start_time))

# Compute Normalized Root Mean Squared Error after denoising.
nrmse = svmbir.phantom.nrmse(phantom_denoised, phantom)


# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/3d_shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display noisy phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom with nosie.'
plot_image(phantom_noisy[display_slice], title=title, filename='output/3d_shepp_logan_phantom_noisy.png', vmin=vmin, vmax=vmax)

# display denoised reconstruction
title = f'Slice {display_slice:d} of denoised Phantom with NRMSE={nrmse:.3f}.'
plot_image(phantom_denoised[display_slice], title=title, filename='output/3d_shepp_logan_denoised.png', vmin=vmin, vmax=vmax)


input("press Enter")