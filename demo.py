
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('data/sinodata.npy')
weight = np.load('data/weightdata.npy')

(num_views, num_slices, num_channels) = sino.shape
angles = np.linspace(0, np.pi, num_views, endpoint=False)

x = svmbir.recon(sino, angles, weight, num_threads=20,
    center_offset=-6, img_downsamp=4,
    sigma_x=0.6350, T=0.000478, max_iterations=10)

proj = svmbir.project(angles, x, num_threads=20,
    center_offset=-6, img_downsamp=4)


## display output #################################
imgplot = plt.imshow(x[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('data/recon.png')
plt.close()

imgplot = plt.imshow(np.swapaxes(sino, 0, 1)[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('data/sino.png')
plt.close()

imgplot = plt.imshow(np.swapaxes(sino-proj, 0, 1)[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('data/err_sino.png')
plt.close()