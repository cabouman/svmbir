import numpy as np
import matplotlib.pyplot as plt
import svmbir

num_rows = 512
num_cols = num_rows
num_views = 288

image = svmbir.phantom.gen_shepp_logan(num_rows)
image = np.expand_dims(image, axis=0)

angles = np.linspace(-np.pi / 2.0, np.pi / 2.0, num_views, endpoint=False)
sino = svmbir.project(angles, image, max(num_rows, num_cols))

(num_views, num_slices, num_channels) = sino.shape

x = svmbir.recon(sino, angles,snr_db=40.0)

x_sharp = svmbir.recon(sino, angles, sharpness=2.0,snr_db=40.0)

## display output for recon #################################
imgplot = plt.imshow(x[0],vmin=0.95,vmax=1.1)
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('output/simple_recon.png')
plt.close()
rmse_x=np.sqrt(np.linalg.norm(x[0]-image[0])**2/(image.shape[1]*image.shape[2]))
print('RMSE for recon:', rmse_x)

## display output for recon with sharpness=2.0 #################################
imgplot = plt.imshow(x_sharp[0],vmin=0.95,vmax=1.1)
imgplot.set_cmap('gray')
plt.colorbar()
plt.savefig('output/simple_recon_sharp.png')
plt.close()
rmse_x_sharp=np.sqrt(np.linalg.norm(x_sharp[0]-image[0])**2/(image.shape[1]*image.shape[2]))
print('RMSE for recon with sharpness=2.0:', rmse_x_sharp)