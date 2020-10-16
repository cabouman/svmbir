
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('sinodata.npy')

(num_views, num_slices, num_channels) = sino.shape
angles = np.linspace(0, np.pi, num_views, endpoint=False)

# center_offset accounts for the center of rotation being offset from the center of the detector by 6 detector channels
x = svmbir.recon(sino, angles, center_offset=-6)

x_sharp = svmbir.recon(sino, angles, sharpen=2.0, center_offset=-6)

## display output #################################
imgplot = plt.imshow(x[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('recon.png')
plt.close()

## display output #################################
imgplot = plt.imshow(x_sharp[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('recon_sharp.png')
plt.close()
