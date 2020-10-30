========
Overview
========

**svmbir** is a Python implementation of the Super-Voxel Model Based Iterative Reconstruction (MBIR) algorithm :cite:`wang2016high` :cite:`wang2017massively` for fast reconstruction of parallel beam 3D data.

The code performs Bayesian reconstruction of tomographic data, so it is particularly well-suited for sparse view reconstruction from noisy data. It also has hooks to support Plug-and-Play prior models that can dramatically improve image quality :cite:`venkatakrishnan2013plug` :cite:`sreehari2016plug`. 


**Conversion from Arbitray Length Units (ALU):**

In order to simplify usage, reconstructions are done using arbitrary units (ALU). In this system, 1 ALU can correspond to any convenient measure of distance chosen by the user. So for example, it is often convenient to take 1 ALU to be the distance between pixels, which by default is also taken to be the distance between detector channels.


_Transmission CT Example:_ For this example, assume that the physical spacing between detector channels is 5 mm. In order to simplify our calculations, we also use the default detector channel spacing and voxel spacing of ``delta_channel=1.0`` and ``delta_xy=1.0``. In other words, we have adopted the convention that the voxel spacing is 1 ALU = 5 mm, where 1 ALU is now our newly adopted measure of distance.

Using this convention, the 3D reconstruction array, ``image``, will be in units of :math:`mbox{ALU}^{-1}`. However, the image can be converted back to more conventional usits of :math:`\mbox{mm}^{-1}` using the following equation:

.. math::

    \mbox{image in mm$^{-1}$} = \frac{ \mbox{image in ALU$^{-1}$} }{ 5 \mbox{mm} / \mbox{ALU}}


_Emission CT Example:_ Once again, we assume that the channel spacing in the detector is 5 mm, and we again adopt the default reconstruction parameters of ``delta_channel=1.0`` and ``delta_xy=1.0``. Then we once again have that 1 ALU = 5 mm. 

Using this convention, the 3D array, ``image``, will be in units of photons/AU. However, the image can be again converted to units of photons/mm using the following equation:

.. math::

    \mbox{image in photons/mm} = \frac{ \mbox{image in photons/ALU} }{ 5 \mbox{mm} / \mbox{ALU}}
