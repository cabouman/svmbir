======
Theory
======

Super-Voxel Model-Based Iterative Reconstruction (SVMBIR) is a fast algorithm for computing MBIR reconstructions from tomographic data.
MBIR reconstruction works by solving the following optimization problem

.. math::

    {\hat x} = \arg \min_x \left\{ f(x) + h(x) \right\}

where :math:`f(x)` is the forward model term and :math:`h(x)` is the prior model term.
The super-voxel algorithm is then used to efficiently perform this optimization.


**Forward Model:**
The forward model term has the form,

.. math::

    f(x) = \frac{1}{2 \sigma_y^2} \Vert y - Ax \Vert_\Lambda^2

where :math:`y` is the sinogram data, 
where :math:`x` is the unknown image to be reconstructed, 
:math:`A` is the linear projection operator for the specified imaging geometry, 
:math:`\Lambda` is the diagonal matrix of sinogram weights, :math:`\Vert y \Vert_\Lambda^2 = y^T \Lambda y`, and :math:`\sigma_y` is a parameter controling the assumed standard deviation of the measurement noise.

These quantities correspond to the following python variables:

* :math:`y` corresponds to ``sino``
* :math:`\sigma_y` corresponds to ``sigma_y`` 
* :math:`\Lambda` corresponds to ``weights`` 

The weights can either be set automatically using the ``weight_type`` input, or they can be explicitly set to an array of precomputed weights.
For many new users, it is easier to use one of the automatic weight settings shown below.

* weight_type="unweighted" => Lambda = 1 + 0*sino
* weight_type="transmission" => Lambda = numpy.exp(-sino)
* weight_type="transmission_root" => Lambda = numpy.exp(-sino/2)
* weight_type="emmission" => Lambda = (1/(sino + 0.1))

Option "unweighted" provides unweighted reconstruction; Option "transmission" is the correct weighting for transmission CT with constant dosage; Option "transmission_root" is commonly used with transmission CT data to improve image homogeneity; Option "emmission" is appropriate for emission CT data. 

**Prior Model:**
The ``svmbir`` function allows the prior model to be set either as a qGGMRF or a proximal map prior. 
The qGGRMF prior is the default method recommended for new users. 
Alternatively, the proximal map prior is an advanced feature required for the implementation of the Plug-and-Play algorithm. The Plug-and-Play algorithm allows the modular use of a wide variety of advanced prior models including priors implemented with machine learning methods such as deep neural networks.

The qGGMRF prior model has the form

.. math::

    h(x) = \sum_{ \{s,r\} \in {\cal P}} b_{s,r} \rho ( x_s - x_r) \ ,

where 

.. math::

    \rho ( \Delta ) = \frac{|\Delta |^p }{ p \sigma_x^p } \left( \frac{\left| \frac{\Delta }{ T \sigma_x } \right|^{q-p}}{1 + \left| \frac{\Delta }{ T \sigma_x } \right|^{q-p}} \right)

where :math:`{\cal P}` represents a 8-point 2D neighborhood of pixel pairs in the :math:`(x,y)` plane and a 2-point neighborhood along the slice axis;
:math:`\sigma_x` is the primary regularization parameter;
:math:`b_{s,r}` controls the neighborhood weighting;
:math:`p<q=2.0` are shape parameters;
and :math:`T` is a threshold parameter.

These quantities correspond to the following python variables:

* :math:`\sigma_x` corresponds to ``sigma_x``
* :math:`p` corresponds to ``p`` 
* :math:`q` corresponds to ``q`` 
* :math:`T` corresponds to ``T`` 


**Proximal Map Prior:**
The proximal map prior is provided as a option for advanced users would would like to use plug-and-play methods.
If ``prox_image`` is supplied, then the proximal map prior model is used, and the qGGMRF parameters are ignored. 
In this case, the reconstruction solves the optimization problem:

.. math::

    {\hat x} = \arg \min_x \left\{ f(x) + \frac{1}{2\sigma_p^2} \Vert x -v \Vert^2 \right\}

where the quantities correspond to the following python variables:

* :math:`v` corresponds to ``prox_image``
* :math:`\sigma_p` corresponds to ``sigma_p``

