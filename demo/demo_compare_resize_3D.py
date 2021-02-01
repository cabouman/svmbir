import os
import numpy as np
from svmbir.phantom import plot_image
import svmbir

# from skimage.transform import resize
import skimage
import PIL

import timeit

def PIL_resize_3D(recon, output_shape):

    recon_resized_list = []
    for i in range(recon.shape[0]):
        PIL_image = PIL.Image.fromarray(recon[i])
        PIL_image_resized = PIL_image.resize((output_shape[1],output_shape[0]), resample=PIL.Image.BILINEAR)
        recon_resized_list.append(np.asarray(PIL_image_resized))

    return np.stack(recon_resized_list, axis=0)


def sk_resize_3D(recon, output_shape):

    recon = np.transpose(recon, (1, 2, 0))
    recon = skimage.transform.resize(recon, output_shape)
    recon = np.transpose(recon, (2, 0, 1))

    return recon

num_rows = 256
num_cols = 64
num_slices = 33


# Display parameters
vmin = 0.0
vmax = 1.1
display_slice = 16

img = svmbir.phantom.gen_microscopy_sample_3d(num_rows,num_cols,num_slices)

output_shape = (100,25)
# output_shape = (255,64)

start = timeit.default_timer()
img_resized_sk = sk_resize_3D(img, output_shape)
time_sk = timeit.default_timer()

start = timeit.default_timer()
img_resized_PIL = PIL_resize_3D(img, output_shape)
time_PIL = timeit.default_timer()

plot_image(img[display_slice], title='original', filename='output/3D_resize_original.png', vmin=vmin, vmax=vmax)
plot_image(img_resized_sk[display_slice], title='img_resized_sk', filename='output/3D_resize_img_sk.png', vmin=vmin, vmax=vmax)
plot_image(img_resized_PIL[display_slice], title='img_resized_PIL', filename='output/3D_resize_img_PIL.png', vmin=vmin, vmax=vmax)

print("Original shape: {}".format(img.shape))
print("skimage resized shape: {}".format(img_resized_sk.shape))
print("PIL resized shape: {}".format(img_resized_PIL.shape))

print("skimage time: {}".format(time_sk))
print("PIL time: {}".format(time_PIL))

