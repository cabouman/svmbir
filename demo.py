
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('data/sinodata.npy')
weight = np.load('data/weightdata.npy')

(NViews, NSlices, NChannels) = sino.shape
angles = np.linspace(0, np.pi, NViews, endpoint=False)

x = svmbir.recon(angles, sino, weight, num_threads=20,
    CenterOffset=-6, img_downsamp=4,
    SigmaX=0.6350, T=0.000478, MaxIterations=10)

proj = svmbir.project(angles, x, num_threads=20,
    CenterOffset=-6, img_downsamp=4)


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