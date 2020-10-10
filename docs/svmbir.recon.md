# ``svmbir.recon``

**Signature:**

	svmbir.recon( 
		sino,
		angles,

		delta_channel=1.0,
		center_offset=0.0,

		delta_pixel=1.0,
		num_row=None,
		num_col=None,
		roi_radius=None,

		sigma_y=None,
		snr_db=30.0,
		weights=None,
		weight_type="unweighted",

		sharpen=1.0,
		sigma_x=None,
		positivity=True,
		p=1.2,
		q=2.0,
		T=1.0,
		b_interslice=1.0, 

		prox_image=None,

		init_image=0.0001,
		init_proj=None,
		stop_threshold=0.0,
		max_iterations=20,
		num_threads=1,
		delete_temps=True,
		svmbir_lib_path=`~/.cache/svmbir_lib`
	) 

Computes the 3D MBIR reconstruction using a parallel beam geometry and other parameters as described below. MBIR reconstruction works by solving the following optimization problem
$$
{\hat x} = \arg \min_x \left\{ f(x) + h(x) \right\}
$$
where 
$$
f(x) = \frac{1}{2 \sigma_x^2} \Vert y - Ax \Vert_\Lambda^2
$$
is the forward model and $h(x)$ is the prior model that regularizes the solution. The forward model parameters include the sinogram data, $y$, the parallel beam projector, $A$, the scaling parameter, $\sigma_y$, and the sinogram weights, $\Lambda$. 

The ``svmbir`` function allows the prior model to be set either as a qGGMRF or a proximal map prior. The qGGRMF prior is the default method recommended for new users. Alternatively, the proximal map prior is an advanced feature required for the implementation of the Plug-and-Play algorithm. The Plug-and-Play algorithm allows the modular use of a wide variety of advanced prior models including priors implemented with machine learning methods such as deep neural networks.

**Required Parameters:**

 * ``sino``: 3D numpy array of sinogram data with shape ``[num_view,num_slice,num_channel]``.

For transmission CT, the sinogram entries are typically computed as $
y_i = -\log \left( \lambda_i / \lambda_{0,i} \right)$ where $\lambda_i$ is the photon count for the $i^{th}$ object projection and $\lambda_{i,0}$ is the photon count for the corresponding blank scan measurement. For emission scans, the sinogram entries are typically integrated photon counts through an object.

 * ``angles``: 1D numpy array of view angles in radians. 

The 1D array is organized so that ``angles[k]`` is the angle in radians for view ``k``. 

**Sinogram Parameters:**

 * ``delta_channel``: [Default=1.0] Scalar value of detector channel spacing in ALU.

 * ``center_offset``: [Default=0.0] Scalar value of offset from center-of-rotation.

The offset in the center of rotation in units of number of detector channels from the center of detector. This value can be factional.

**Image Parameters:**

 * ``delta_pixel``: [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in ALU.

 * ``num_row``: [Default=None] Integer number of rows in reconstructed image. If ``None``, automatically set by calling ``svmbir.auto_num_row``.

 * ``num_col``: [Default=None] Integer number of columns in reconstructed image. If ``None``, automatically set by calling ``svmbir.auto_num_col``.

 * ``roi_radius``: [Default=None] Scalar value of radius of reconstruction in ALU. If ``None``, automatically set by calling ``svmbir.auto_roi_radius``.
 
The angle=0 corresponds to integration along the $x$ coordinate, i.e., along rows of the reconstruction. The image defaults to a size large enough to include the entire detector array. Pixels outside the radius ``roi_radius`` in the $(x,y)$ plane are disregarded in initialization and reconstruction. The automatically set size of ``roi_radius`` is choosen so that it inscribes the largest axis of the recon image with a shape ``[num_slices,num_row,num_col]``.

**Forward Model Parameters:**

 * ``sigma_y``: [Default=None] Scalar value of noise standard deviation parameter. If ``None``, automatically set by calling ``svmbir.auto_sigma_y``.

 * ``snr_db``: [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB. Ignored if ``sigma_y`` is not ``None``.

 * ``weights``: [Default=None] 3D numpy array of weights with same shape as ``sino``. 

 * ``weight_type``: [Default=0] Type of noise model used for data. Ignored if ``weights`` parameter is supplied. Can be set to the values ``unweighted``, ``transmission``, ``transmission_root``, and ``emission``. 

If 3D array ``weights`` is not supplied, then the parameter ``weight_type`` determines the weights used in the forward model according to the following table:
	
	weight_type="unweighted" => Lambda = numpy.ones_like(sino)
	weight_type="transmission" => Lambda = numpy.exp(-sino)
	weight_type="transmission_root" => Lambda = numpy.exp(-sino/2)
	weight_type="emmission" => Lambda = (1/(sino + 0.1))

Option "unweighted" provides unweighted reconstruction; Option "transmission" is the correct weighting for transmission CT with constant dosage; Option "transmission_root" is commonly used with transmission CT data to improve image homogeneity; Option "emmission" is appropriate for emission CT data. 

**qGGMRF Prior Model Parameters:**

 * ``sharpen``: [Default=1.0] Scalar value that controls level of sharpening. Large value results in sharper or less regularized reconstruction. Ignored if ``sigma_x`` is not ``None``.

  * ``sigma_x``: [Default=None] Scalar value >0 that specifies the qGGMRF scale parameter. If ``None``, automatically set by calling ``svmbir.auto_sigma_x``.

 * ``positivity``: [Default=True] Boolean value that determines if positivity constraint is enforced.

 * ``p``: [Default=1.2] Scalar value >1 that specifies the qGGMRF shape parameter.

 * ``q``: [Default=2.0] Scalar value >``p`` that specifies the qGGMRF shape parameter.

 * ``T``: [Default=1.0] Scalar value >0 that specifies the qGGMRF threshold parameter.

 * ``b_interslice``: [Default=1.0] Scalar value >0 that specifies the interslice regularization. Default value of 1 is best in most cases.

The parameter ``sharpen`` can be used to control the level of regularization of the reconstructed image. Large values of ``sharpen`` will result in a less regularized or sharper image and smaller values will result in a more regularized or smoother image. The parameter ``sigma_x`` can be used to directly control regularization, but this is only recommended for expert users. The ``positivity`` parameter defaults to True; however, it should be changed to False when used in applications that can generate negative image values. The default values of ``p``, ``q``, ``T`` and ``b_interslice`` should be fine for most applications. However, ``b_interslice`` can be increased to values >1 in order to increase regularization along the slice axis.

For reference, the qGGMRF prior model has the form
$$
h(x) = \sum_{ \{s,r\} \in {\cal P}} b_{s,r} \rho ( x_s - x_r) \ ,
$$
where 
$$
\rho ( \Delta ) = \frac{|\Delta |^p }{ p \sigma_x^p } \left( \frac{\left| \frac{\Delta }{ T \sigma_x } \right|^{q-p}}{1 + \left| \frac{\Delta }{ T \sigma_x } \right|^{q-p}} \right)
$$
where ${\cal P}$ represents 8-point pixel pair neighbors in the $(x,y)$ plane and 2-point neighbors along the slice axis, $\sigma_x$=``sigma_x``, $T$=``T``, $\sigma_x$=``sigma_x``, and ``b_interslice`` controls the relative amplitude of $b_{s,r}$ along the slice axis.

**Proximal Map Prior Parameters:**

 * ``prox_image``: [Default=None] 3D numpy array with proximal map input image. 

If ``prox_image`` is supplied, then the proximal map prior model is used, and the qGGMRF parameters are ignored. The proximal map prior is required when ``svmbir.recon`` is used with Plug-and-Play. In this case, the reconstruction solves the optimization problem:
$$
{\hat x} = \arg \min_x \left\{ \frac{1}{2} \Vert y - Ax \Vert_\Lambda^2 + \frac{1}{2\sigma_x^2} \Vert x -v \Vert^2 \right\}
$$
where $v$ is given by ``prox_image``. This feature should only be used by expert users since ``svmbir`` must be incorporated in a Plug-and-Play outter loop in order to make the option useful.

**Advanced Parameters:**

 * ``init_image``: [Default=0.0001] Initial value of reconstruction image specified by either a single scalar value or a 3D numpy array with a shape of ``(shape.sino[1],num_row,num_col)``.

 * ``init_proj``: [Default=None] Initial value of forward projection of the ``init_image``. This can be used to reduce computation for the first iteration when using the proximal map option.

 * ``stop_threshold``: [Default=0.0] Scalar valued stopping threshold in percent. If ``stop_threshold=0``, then run max iterations.

 * ``max_iterations``: [Default=20] Integer valued specifying the maximum number of iterations.

 * ``num_threads``: [Default=1] Number of compute threads requested when executed.

 * ``delete_temps``: [Default=True] Delete temporary files used in computation.

 * ``svmbir_lib_path``: [Default=`~/.cache/svmbir_lib`] Path to directory containing library of forward projection matrices.

**Returns:**

 * ``image``: 3D numpy array with reconstruction image in units of ALU$^{-1}$.

The 3D ``image`` array is a reconstruction with a shape of ``[sino.shape[1],num_row,num_col]`` where ``sino.shape[1]`` is the number of sinogram slices. The reconstruction is 0 outside the ROI as defined by ``roi_radius``.


#Example Usage:

