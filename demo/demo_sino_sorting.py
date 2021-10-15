import os
import numpy as np
import svmbir
import time
from demo_utils import plot_image
import matplotlib.pyplot as plt

"""
This is a test to compare performance of SVMBIR using Golden Section and sorted view angle ordering of sinogram data
"""
print('\n\n**This is a test to compare performance of SVMBIR using Golden Section and sorted view angle ordering of sinogram data.\n')


# Simulated image parameters
num_rows_cols = 256 # Assumes a square image
num_slices = 33
display_slice = 12 # Display slice at z=-0.25

# Simulated sinogram parameters
num_views = 144

# Reconstruction parameters
T = 0.1
p = 1.1
sharpness = 0.0
snr_db = 40.0

# Display parameters
vmin = 1.0
vmax = 1.2

# Generate phantom
phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows_cols, num_rows_cols, num_slices)

# Generate array of view angles using Golden Section method of Kohler IEEE Symposium Conference Record Nuclear Science 2004. 
g = (np.sqrt(5)-1)/2
angles_original = g * np.pi * np.arange(num_views)

# Generate sinogram by projecting phantom
sino_original = svmbir.project(phantom, angles_original, num_rows_cols)

weights_original = svmbir.calc_weights(sino_original, weight_type='transmission')

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino_original.shape

# Test sino_sort with 2 arguments
sino_sorted, angles_sorted = svmbir.sino_sort(sino_original, angles_original)

# Test sino_sort with 3 arguments
sino_sorted, angles_sorted, weights_sorted = svmbir.sino_sort(sino_original, angles_original, weights_original)


print('Starting recon with Golden Section view sampling (i.e., original).\n')

# Perform MBIR reconstruction with original data
start_original = time.time()
recon_original = svmbir.recon(sino_original, angles_original, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_original = time.time()


print('Starting recon with sorted view sampling.\n')

# Perform MBIR reconstruction with sorted data
start_sorted = time.time()
recon_sorted = svmbir.recon(sino_sorted, angles_sorted, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_sorted = time.time()


# display reconstruction time
print('\n\n')
print('Processing time for original: ', end_original-start_original, 's')
print('Processing time for sorted: ', end_sorted-start_sorted, 's')

# display nrmse of recon and weights before and after sorting
print('NRMSE between reconstructions using original and sorted reconstructions = ', svmbir.phantom.nrmse(recon_original, recon_sorted))
print('\n\n')


# create output folder
os.makedirs('output', exist_ok=True)

# Plot angle orders for original and sorted
plt.title('Angle orders for original and sorted')
plt.xlabel('Order')
plt.ylabel('Angle (Rad)')
plt.plot(angles_original, '.-', label='Original')
plt.plot(angles_sorted, label='Sorted')
plt.legend()
plt.savefig('output/angle_orders.png')
plt.show()

# Plot angle orders for original mod 2pi and sorted
plt.figure()
plt.title('Angle orders for different approaches')
plt.xlabel('Order')
plt.ylabel('Angle (Rad)')
plt.plot(np.mod(angles_original,2*np.pi), '.-', label='Original Mod 2pi')
plt.plot(angles_sorted, label='Sorted')
plt.legend()
plt.savefig('output/angle_orders_mod2pi.png')
print('close figure to proceed')
plt.show()


# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/3d_shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with original data
title = f'Slice {display_slice:d} of 3D Recon of the original data.'
plot_image(recon_original[display_slice], title=title, filename='output/3d_shepp_logan_recon_original.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with sorted data
title = f'Slice {display_slice:d} of 3D Recon of the sorted data.'
plot_image(recon_sorted[display_slice], title=title, filename='output/3d_shepp_logan_recon_sorted.png', vmin=vmin, vmax=vmax)

# display diff image of reconstructions using original and sorted sinogram
title = f'Diff image between recon with original and sorted sinogram.'
diff_orig_sorted = recon_original - recon_sorted
plot_image(diff_orig_sorted[display_slice], title=title, filename='output/diff_recon_orig_sorted.png', vmin=-vmax/100., vmax=vmax/100.)

input("press Enter")

