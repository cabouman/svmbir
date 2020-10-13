# ``svmbir.auto_sigma_x``

**Signature:**

	svmbir.auto_sigma_x( 
		sino,
		delta_channel=1.0, 
		sharpen=1.0,
	) 

Computes the automatic value of the regularization parameters ``sigma_x`` for use in MBIR reconstruction. 

**Parameters:**

 * ``sino``: 3D numpy array of sinogram data organized with ``sino[slice,channel,view]``.

 * ``delta_channel``: [Default=1.0] Scalar value of detector channel spacing in ALU.

 * ``sharpen``: [Default=1.0] Scalar value that controls level of sharpening. Large value results in sharper or less regularized reconstruction.


**Returns:**

 * ``sigma_x``: Automatic value of regularization parameter.

# What it does:

This function computes a automatic value for the regularization parameter ``sigma_x`` using the formula:

	[num_view,num_slice,num_channel] = sino.shape
	sino_ave = numpy.mean(sino)
	sigma_x = 0.1 * sharpen * ( sino_ave / ( num_channel * delta_channel ) )

The reconstruction can be sharpened (i.e., reduced regularization) by increasing ``sharpen``, and it can be made softer (i.e., decreased regularization) by reducing its value.

#Example Usage:



