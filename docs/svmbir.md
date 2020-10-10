# Overview of svmbir.py

**svmbir** is a Python implementation of the Super-Voxel Model Based Iterative Reconstruction (MBIR) algorithm [1,2] for fast reconstruction of parallel beam 3D data.

The code performs Bayesian reconstruction of tomographic data, so it is particularly well-suited for sparse view reconstruction from noisy data. It also has hooks to support Plug-and-Play prior models that can dramatically improve image quality [3,4]. 

**Functions:**

>[svmbir.recon](./svmbir.recon.md): Computes MBIR reconstruction from sinogram data

>[svmbir.project](./svmbir.project.md): Computes forward projection of an image

>[svmbir.calc\_weights](./svmbir.calc\_weights.md): Calculate the weights used in reconstruction.
>

>[svmbir.auto\_sigma\_x](./svmbir.auto\_sigma\_x.md): Automatically sets the ``sigma_x`` regularization parameter

>[svmbir.auto\_sigma\_y](./svmbir.auto\_sigma\_y.md): Automatically sets the ``sigma_y`` noise parameter

>[svmbir.auto\_num\_row](./svmbir.auto\_num\_row.md): Automatically sets ``num_row`` the number of rows in the reconstruction

>[svmbir.auto\_num\_col](./svmbir.auto\_num\_col.md): Automatically sets ``num_col`` the number of columns in the reconstruction

>[svmbir.auto\_roi\_radius](./svmbir.auto\_roi\_radius.md): Automatically sets ``roi_radius`` the region of interest radius.


**Conversion from Arbitray Length Units (ALU):**

In order to simplify usage, reconstructions are done using arbitrary units (ALU). In this system, 1 ALU can correspond to any convenient measure of distance chosen by the user. So for example, it is often convenient to take 1 ALU to be the distance between pixels, which by default is also taken to be the distance between detector channels.


_Transmission CT Example:_ For this example, assume that the physical spacing between detector channels is 5 mm. In order to simplify our calculations, we also use the default detector channel spacing and voxel spacing of ``delta_channel=1.0`` and ``delta_xy=1.0``. In other words, we have adopted the convention that the voxel spacing is 1 ALU = 5 mm, where 1 ALU is now our newly adopted measure of distance.

Using this convention, the 3D reconstruction array, ``image``, will be in units of ALU$^{-1}$. However, the image can be converted back to more conventional usits of mm$^{-1}$ using the following equation:
$$
(\mbox{image in mm$^{-1}$}) = \frac{ (\mbox{image in ALU$^{-1}$}) }{ 5 \mbox{mm} / \mbox{ALU}}
$$

_Emission CT Example:_ Once again, we assume that the channel spacing in the detector is 5 mm, and we again adopt the default reconstruction parameters of ``delta_channel=1.0`` and ``delta_xy=1.0``. Then we once again have that 1 ALU = 5 mm. 

Using this convention, the 3D array, ``image``, will be in units of photons/AU. However, the image can be again converted to units of photons/mm using the following equation:
$$
(\mbox{image in photons/mm}) = \frac{ (\mbox{image in photons/ALU}) }{ 5 \mbox{mm} / \mbox{ALU}}
$$


**References:** 

[1] Xiao Wang, Amit Sabne, Sherman Kisner, Anand Raghunathan, Charles Bouman, and Samuel Midkiff, High Performance Model Based Image Reconstruction", 21st ACM SIGPLAN Symposium on Principles and Practice of Parallel Programming (PPoPP '16), March 12-16, 2016.

[2] Xiao Wang, Amit Sabne, Putt Sakdhnagool, Sherman J. Kisner, Charles A. Bouman, and Samuel P. Midki, "Massively Parallel 3D Image Reconstruction", 2017 Supercomputing Conference (SC17), ACM, November 13-16, 2017.

[3] Singanallur V. Venkatakrishanan, Charles A. Bouman, and Brendt Wohlberg, "Plug-and-Play Priors for Model Based Reconstruction," 2013 IEEE Global Conference on Signal and Information Processing (GlobalSIP), Austin, Texas, USA, December 3-5, 2013.

[4] Suhas Sreehari, S. Venkat Venkatakrishnan, Brendt Wohlberg, Gregery T. Buzzard, Lawrence F. Drummy, Jeffrey P. Simmons, and Charles A. Bouman, "Plug-and-Play Priors for Bright Field Electron Tomography and Sparse Interpolation," IEEE Transactions on Computational Imaging, vol. 2, no. 4, Dec. 2016.
