import os
import numpy as np
from svmbir.phantom import plot_image
import svmbir

import PIL
from skimage.transform import resize

num_rows = 256
num_cols = 64

# Display parameters
vmin = 0.0
vmax = 1.1

# Generate phantom with a single slice
img = svmbir.phantom.gen_microscopy_sample(num_rows,num_cols)

output_shape = (100,25)
# output_shape = (255,64)


img_resized_sk = resize(img, output_shape)

PIL_image = PIL.Image.fromarray(img)
PIL_image_resized = PIL_image.resize((output_shape[1],output_shape[0]), resample=PIL.Image.BILINEAR)
img_resized_PIL = np.asarray(PIL_image_resized)

plot_image(img, title='original', filename='output/original.png', vmin=vmin, vmax=vmax)
plot_image(img_resized_sk, title='img_resized_sk', filename='output/img_resized_sk.png', vmin=vmin, vmax=vmax)
plot_image(img_resized_PIL, title='img_resized_PIL', filename='output/img_resized_PIL.png', vmin=vmin, vmax=vmax)

print(img_resized_sk.shape)
print(img_resized_PIL.shape)