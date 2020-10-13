
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('sinodata.npy')
weights = np.load('weightdata.npy')

(num_views, num_slices, num_channels) = sino.shape
angles = np.linspace(0, np.pi, num_views, endpoint=False)

x = svmbir.recon(sino, angles, num_threads=20,
    center_offset=-6, T=0.000478, max_iterations=10)


## display output #################################
imgplot = plt.imshow(x[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('recon.png')
plt.close()
