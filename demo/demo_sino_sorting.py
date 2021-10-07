import os
import numpy as np
import svmbir
import time
from demo_utils import plot_image
import matplotlib.pyplot as plt

"""
This is a test to compare performance of SVMBIR  for original, shuffled, and sorted (in terms of angles) sinogram data 
"""

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

# Generate array of view angles form 0 to 180 degs
angles_original = np.linspace(0, np.pi, num_views, endpoint=False)

# create output folder
os.makedirs('output', exist_ok=True)

# Set up plot to show angle orders for different approaches
plt.title('Angle orders for different approaches')
plt.xlabel('Order')
plt.ylabel('Angle (Rad)')
plt.plot(angles_original, label='Original')

# Generate sinogram by projecting phantom
sino_original = svmbir.project(phantom, angles_original, num_rows_cols)

weights_original = svmbir.calc_weights(sino_original, weight_type='transmission')

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino_original.shape

# Perform fixed resolution MBIR reconstruction with original data
start_original = time.time()
recon_original = svmbir.recon(sino_original, angles_original, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_original = time.time()

# Shuffle the angles and corresponding data
idx = np.arange(0, num_views, 1)
np.random.shuffle(idx)
angles_shuffled = angles_original[idx]
sino_shuffled = sino_original[idx]
weights_shuffled = weights_original[idx]
print('Shuffled angles object id: ', id(angles_shuffled))
print('Shuffled sinogram object id: ', id(sino_shuffled))
print('Shuffled weights object id: ', id(weights_shuffled))
plt.plot(angles_shuffled, label='Shuffled')

# Perform fixed resolution MBIR reconstruction with shuffled data
start_shuffled = time.time()
recon_shuffled = svmbir.recon(sino_shuffled, angles_shuffled, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_shuffled = time.time()

# Sort the angles and corresponding data to ascending order
sino_sorted, angles_sorted, weights_sorted = svmbir.sino_sort(sino_shuffled, angles_shuffled, weights_shuffled)
print('Sorted angles object id: ', id(angles_sorted))
print('Sorted sinogram object id: ', id(sino_sorted))
print('Sorted weights object id: ', id(weights_sorted))
plt.plot(angles_sorted, label='Sorted')

# Perform fixed resolution MBIR reconstruction with sorted data
start_sorted = time.time()
recon_sorted = svmbir.recon(sino_sorted, angles_sorted, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_sorted = time.time()

# Plot angle orders for different approaches
plt.legend()
plt.savefig('output/angle_orders.png')
input("press Enter to continue")

# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/3d_shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with original data
title = f'Slice {display_slice:d} of 3D Recon of the original data.'
plot_image(recon_original[display_slice], title=title, filename='output/3d_shepp_logan_recon_original.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with shuffled data
title = f'Slice {display_slice:d} of 3D Recon of the shuffled data.'
plot_image(recon_shuffled[display_slice], title=title, filename='output/3d_shepp_logan_recon_shuffled.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with sorted data
title = f'Slice {display_slice:d} of 3D Recon of the sorted data.'
plot_image(recon_sorted[display_slice], title=title, filename='output/3d_shepp_logan_recon_sorted.png', vmin=vmin, vmax=vmax)

# display diff image of reconstructions using original and shuffled sinogram
title = f'Slice {display_slice:d} of Diff image between reconstructions with original and shuffled sinogram.'
diff_orig_shuffled = recon_original - recon_shuffled
plot_image(diff_orig_shuffled[display_slice], title=title, filename='output/diff_recon_orig_shuffled.png', vmin=-vmax/100., vmax=vmax/100.)

# display diff image of reconstructions using shuffled and sorted sinogram
title = f'Slice {display_slice:d} of Diff image between reconstructions with shuffled and sorted sinogram.'
diff_shuffled_sorted = recon_shuffled - recon_sorted
plot_image(diff_shuffled_sorted[display_slice], title=title, filename='output/diff_recon_orig_sorted.png', vmin=-vmax/100., vmax=vmax/100.)

# display reconstruction time
print('Processing time for original: ', end_original-start_original, 's')
print('Processing time for shuffled: ', end_shuffled-start_shuffled, 's')
print('Processing time for sorted: ', end_sorted-start_sorted, 's')

# display nrmse of recon and weights before and after sorting
print('NRMSE between original and shuffled sinogram = ', svmbir.phantom.nrmse(sino_original, sino_sorted))
print('NRMSE between reconstructions using original and shuffled sinogram = ', svmbir.phantom.nrmse(recon_original, recon_shuffled))
print('NRMSE between reconstructions using shuffled and sorted sinogram = ', svmbir.phantom.nrmse(recon_shuffled, recon_sorted))
print('NRMSE between original weights and sorted weights = ', svmbir.phantom.nrmse(weights_original, weights_sorted))


input("press Enter")

