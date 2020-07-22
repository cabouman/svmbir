
import numpy as np
import matplotlib.pyplot as plt

import svmbir


sino = np.load('data/sinodata.npy')
weight = np.load('data/weightdata.npy')

print(sino.shape)

# svmbir_lib : contains system matrix : defaults to ~/svmbir_lib directory
# delete everything else by default

# x = svmbir.recon(sino, wght, angles, SigmaX=0.6350, T=0.000478, svmbir_lib=/depot/user/smajee/svmbir_lib)
# x = svmbir.recon(sino, wght, angles, SigmaX=0.6350, T=0.000478)


mbir_data_path='data/sv-mbirct_data/'
NViews = 288
NSlices = 1
NChannels = 512

angles = np.linspace(0, np.pi, NViews, endpoint=False)

svmbir.gen_sysmatrix(mbir_data_path,
                angles=angles, NChannels=NChannels, NViews=NViews, NSlices=NSlices, 
                CenterOffset=-6, img_downsamp=4)

x = svmbir.run_recon(mbir_data_path, 
                sino=sino, wght=weight, SigmaX=0.6350, T=0.000478)

# display reconstruction
imgplot = plt.imshow(x[0])
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('data/recon.png')
plt.show()

