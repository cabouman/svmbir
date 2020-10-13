
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('sinodata.npy')

(num_views, num_slices, num_channels) = sino.shape
angles = np.linspace(0, np.pi, num_views, endpoint=False)

x = svmbir.recon(sino, angles, snr_db=50.0,
    center_offset=-6,
	num_threads=20, max_iterations=20)

# x = svmbir.recon(sino, angles, weight_type='transmission', num_threads=20,
#     center_offset=-6, sigma_y=1,
#     sigma_x=0.6350, T=0.000478, max_iterations=10)

## display output #################################
imgplot = plt.imshow(x[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('recon.png')
plt.close()
