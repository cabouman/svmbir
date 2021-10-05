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
tilt_angle = np.pi/2 # Tilt range of +-90deg

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

# Generate array of view angles form -90 to 90 degs
angles = np.linspace(-tilt_angle, tilt_angle, num_views, endpoint=False)

# Set up plot to show angle orders for different approaches
plt.title('Angle orders for different approaches')
plt.xlabel('Order')
plt.ylabel('Angle (Rad)')
plt.plot(angles, label='Original')

# Generate sinogram by projecting phantom
sino = svmbir.project(angles, phantom, num_rows_cols)
print('Original sinogram memory address: ', id(sino))

# Determine resulting number of views, slices, and channels
(num_views, num_slices, num_channels) = sino.shape

# Perform fixed resolution MBIR reconstruction with original data
start_original = time.process_time()
recon_original = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_original = time.process_time()

# Compute Normalized Root Mean Squared Error with original data
nrmse_original = svmbir.phantom.nrmse(recon_original, phantom)

# Shuffle the angles and corresponding data
idx = np.arange(0, num_views, 1)
np.random.shuffle(idx)
angles = angles[idx]
sino = sino[idx]
print('Shuffled sinogram memory address: ', id(sino))
plt.plot(angles, label='Shuffled')

# Perform fixed resolution MBIR reconstruction with shuffled data
start_shuffled = time.process_time()
recon_shuffled = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_shuffled = time.process_time()

# Compute Normalized Root Mean Squared Error with shuffled data
nrmse_shuffled = svmbir.phantom.nrmse(recon_shuffled, phantom)

# Sort the angles and corresponding data to ascending order
sino, angles, weights = svmbir.sino_sort(sino, angles)
print('Sorted sinogram memory address: ', id(sino))
plt.plot(angles, label='Sorted')

# Perform fixed resolution MBIR reconstruction with sorted data
start_sorted = time.process_time()
recon_sorted = svmbir.recon(sino, angles, T=T, p=p, sharpness=sharpness, snr_db=snr_db)
end_sorted = time.process_time()

# Compute Normalized Root Mean Squared Error with sorted data
nrmse_sorted = svmbir.phantom.nrmse(recon_sorted, phantom)


# Plot angle orders for different approaches
plt.legend()
plt.savefig('output/angle_orders.png')
plt.show()

# create output folder
os.makedirs('output', exist_ok=True)

# display phantom
title = f'Slice {display_slice:d} of 3D Shepp Logan Phantom.'
plot_image(phantom[display_slice], title=title, filename='output/3d_shepp_logan_phantom.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with original data
title = f'Slice {display_slice:d} of 3D Recon of the original data with NRMSE={nrmse_original:.3f}.'
plot_image(recon_original[display_slice], title=title, filename='output/3d_shepp_logan_recon_original.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with shuffled data
title = f'Slice {display_slice:d} of 3D Recon of the shuffled data with NRMSE={nrmse_shuffled:.3f}.'
plot_image(recon_shuffled[display_slice], title=title, filename='output/3d_shepp_logan_recon_shuffled.png', vmin=vmin, vmax=vmax)

# display fix resolution reconstruction with sorted data
title = f'Slice {display_slice:d} of 3D Recon of the sorted data with NRMSE={nrmse_sorted:.3f}.'
plot_image(recon_sorted[display_slice], title=title, filename='output/3d_shepp_logan_recon_sorted.png', vmin=vmin, vmax=vmax)

print('Processing time for original: ', end_original-start_original, 's')
print('Processing time for shuffled: ', end_shuffled-start_shuffled, 's')
print('Processing time for sorted: ', end_sorted-start_sorted, 's')

input("press Enter")

