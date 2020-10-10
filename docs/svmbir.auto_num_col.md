# ``svmbir.auto_num_col``

**Signature:**

	svmbir.auto_num_col( 
		sino
		delta_channel,
		delta_pixel
	) 

Computes the automatic value of ``num_col``, the number of columns in the reconstructed image volume.

**Parameters:**

 * ``sino``: 3D numpy array of sinogram data organized with shape ``[num_view,num_slice,num_channel]``.

 * ``delta_channel``: Scalar value of detector channel spacing in ALU.

 * ``delta_pixel``: Scalar value of the spacing between image pixels in the 2D slice plane in ALU.

**Returns:**

 * ``num_col``: Automatic number of columns.

#What it does:

This function computes the automatic value used for the number of columns in an image, ``num_col`` using the following formula:

	num_channel = sino.shape[2]
	num_col = numpy.ceil( num_channel * (delta_channel/delta_xy) )

#Example Usage:



