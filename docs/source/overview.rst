========
Overview
========

**svmbir** is a Python implementation of the Super-Voxel Model Based Iterative Reconstruction (MBIR) algorithm :cite:`wang2016high` :cite:`wang2017massively` for fast reconstruction of parallel beam 3D data.
The code performs Bayesian reconstruction of tomographic data, so it is particularly well-suited for sparse view reconstruction from noisy data.
It also has hooks to support Plug-and-Play prior models that can dramatically improve image quality :cite:`venkatakrishnan2013plug` :cite:`sreehari2016plug`.

**How does it work?**

The super-voxel code can be 100x to 1000x faster than conventional code because it reorganizes operations in a way that is much better matched to a computer's cache structure. To do this, it precomputes the ``system matrix`` that describes the geometry of the tomography system and stores it in a file in encoded form. Whenever you do a reconstruction with a new geometry, the ``svmbir`` package automatically detects the new geometry, precomputes a new system matrix, and stores it in a library for future use. By default, the system matrices are stored in a subdirectory of your personal ``.cache`` directory in your home directory. So if they are taking too much space on your disk, you can remove these files at any time, and they will just be recomputed when needed.

**Troubleshooting**

*Cached System Matrix Problems:* Rare updates to the software package could include changes to the encoding of the system matrix and result in existing pre-computed matrix files being incompatible after the update. The last such update was on (2020-12-02). To remove the outdated files, delete the cache directory located at ``~/.cache/svmbir``. The package will regenerate the system matrices as needed at the time of reconstruction.

*View Angle Ordering:* It is common practice to collect view data using techniques such as the "golden ratio" method in which the view angles are not collected in monotonically increasing order on the interval :math:`[0,2\pi)`. While ``svmbir`` will produce the correct reconstruction regardless of view ordering, its reconstruction speed will be substantially degraded when the views are not in monotone order. In this case, we highly recommend that users reorder the sinogram views using the provided ``sino_sort`` function. The ``sino_sort``  function first wraps the view angles modulo :math:`2\pi`, and then sorts the views to be in monotonically increasing order by view angle.

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
