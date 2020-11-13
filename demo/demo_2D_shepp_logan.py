import numpy as np
import matplotlib.pyplot as plt

import svmbir

"""
This file demonstrates the generation of a Shepp-Logan phantom followed by sinogram projection and reconstruction using MBIR. 
The phantom, sinogram, and reconstruction are then displayed. 
"""

num_rows = 256
num_cols = num_rows
num_views = 144
threshold = 0.05

# Generate phantom with a single slice
phantom = svmbir.phantom.gen_shepp_logan(num_rows)
phantom = np.expand_dims(phantom, axis=0)

# Generate array of view angles form -180 to 180 degs
angles = np.linspace(-np.pi / 2.0, np.pi / 2.0, num_views, endpoint=False)

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform MBIR reconstruction
recon = svmbir.recon(sino, angles, T=1.0, sharpness=1.0, snr_db=40.0, max_iterations=40)

rmse = np.sqrt(np.linalg.norm(recon[0] - phantom[0]) ** 2 / (recon.shape[1] * phantom.shape[2]))
print(f'The RMSE reconstruction error is {rmse:.3f}.')

# display phantom
imgplot = plt.imshow(phantom[0], vmin=1.0, vmax=1.1)
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('output/shepp_logan_phantom.png')
plt.close()

# display sinogram
imgplot = plt.imshow(np.squeeze(sino))
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('output/shepp_logan_sinogram.png')
plt.close()

# display reconstruction
imgplot = plt.imshow(recon[0], vmin=1.0, vmax=1.1)
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('output/shepp_logan_recon.png')
plt.close()
