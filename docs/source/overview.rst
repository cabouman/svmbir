========
Overview
========

**svmbir** is a Python implementation of the Super-Voxel Model Based Iterative Reconstruction (MBIR) algorithm :cite:`wang2016high` :cite:`wang2017massively` for fast reconstruction of parallel beam 3D data.

The code performs Bayesian reconstruction of tomographic data, so it is particularly well-suited for sparse view reconstruction from noisy data. It also has hooks to support Plug-and-Play prior models that can dramatically improve image quality :cite:`venkatakrishnan2013plug` :cite:`sreehari2016plug`. 

**How does it work?**

The super-voxel code can be 100x to 1000x faster than conventional code because it reorganizes operations in a way that is much better matched to a computer's cache structure. To do this, it precomputes the ``system matrix`` that describes the geometry of the tomography system and stores it in an encoded form. Whenever you do a reconstruction with a new geometry, the ``svmbir`` package automatically detects the new geometry, precomputes a new system matrix, and stores it in a library for future use. By default, the system matrices are stored in a subdirectory of your personal ``.cache`` directory in your home directory. So if they are taking too much space on your disk, you can remove these files at any time, and they will just be recomputed when needed.

**Things to Keep in Mind**

*View Angle Ordering:* Often people will collect tomography data using the "golden ratio" method in which views angles in the range :math:`[0,2\pi]` are collected in a non-sequential way. However, while the svmbir code will reconstruct images with any sequence of view angles, the compute performance will be dramatically degraded if the views angles are not in monotonically increasing order. So we strongly recommend you first wrap your angles using an operation such as :math:`angle\leftarrow angle \mod (2\pi)`, and then sort the angles and corresponding views to be in increasing order.

*Windows Installation:* The package will run under Windows, but there tend to be more things that can go wrong due to the wide variety of configurations that may exist. Make sure to install a 64bit version the the gcc compiler, or it will not be possible to compute large reconstructions without overflowing the resulting 2Gb memory address limit.

**Conversion from Arbitrary Length Units (ALU)**

In order to simplify usage, reconstructions are done using arbitrary length units (ALU). In this system, 1 ALU can correspond to any convenient measure of distance chosen by the user. So for example, it is often convenient to take 1 ALU to be the distance between pixels, which by default is also taken to be the distance between detector channels.


*Transmission CT Example:* For this example, assume that the physical spacing between detector channels is 5 mm. In order to simplify our calculations, we also use the default detector channel spacing and voxel spacing of ``delta_channel=1.0`` and ``delta_xy=1.0``. In other words, we have adopted the convention that the voxel spacing is 1 ALU = 5 mm, where 1 ALU is now our newly adopted measure of distance.

Using this convention, the 3D reconstruction array, ``image``, will be in units of :math:`\mbox{ALU}^{-1}`. However, the image can be converted back to more conventional units of :math:`\mbox{mm}^{-1}` using the following equation:

.. math::

    \mbox{image in mm$^{-1}$} = \frac{ \mbox{image in ALU$^{-1}$} }{ 5 \mbox{mm} / \mbox{ALU}}


*Emission CT Example:* Once again, we assume that the channel spacing in the detector is 5 mm, and we again adopt the default reconstruction parameters of ``delta_channel=1.0`` and ``delta_xy=1.0``. So we have that 1 ALU = 5 mm. 

Using this convention, the 3D array, ``image``, will be in units of photons/AU. However, the image can be again converted to units of photons/mm using the following equation:

.. math::

    \mbox{image in photons/mm} = \frac{ \mbox{image in photons/ALU} }{ 5 \mbox{mm} / \mbox{ALU}}
