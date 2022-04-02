import os
import numpy as np
import matplotlib.pyplot as plt
import svmbir

"""
Fan beam demo
"""

# Simulated sinogram parameters
geometry = 'fan'
dist_source_detector = 1000.0
delta_channel = 1.0
magnification = 2.0
num_views = 512
num_channels = 256
angles = np.linspace(-np.pi, np.pi, num_views, endpoint=False)

# Reconstruction parameters
img_size = 256
sharpness = 0.0
T = 1.0
p = 1.2
snr_db = 40.0

# Generate phantom with a single slice
phantom = svmbir.phantom.gen_shepp_logan(img_size,img_size)
phantom = np.expand_dims(phantom, axis=0)
sino = svmbir.project(phantom, angles, num_channels, geometry=geometry, dist_source_detector=dist_source_detector, magnification=magnification, delta_channel=delta_channel)

# Perform MBIR reconstruction
recon = svmbir.recon(sino, angles, num_rows=img_size, num_cols=img_size, T=T, p=p, sharpness=sharpness, snr_db=snr_db, geometry=geometry, dist_source_detector=dist_source_detector, magnification=magnification, delta_channel=delta_channel)

# Compute Normalized Root Mean Squared Error
nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

#plt.ion()
vmin = 1.0
vmax = 1.2
plt.figure(); plt.imshow(phantom[0],vmin=vmin,vmax=vmax,cmap='gray'); plt.colorbar()
plt.title('Shepp Logan Phantom')

plt.figure(); plt.imshow(np.squeeze(sino).T,cmap='gray'); plt.colorbar()
plt.title('Sinogram')

plt.figure(); plt.imshow(recon[0],vmin=vmin,vmax=vmax,cmap='gray'); plt.colorbar()
plt.title(f'Reconstruction, nmrse={nrmse:.3f}')

print("Close figures to continue")
plt.show()

