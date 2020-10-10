# ``svmbir.auto_num_row``

**Signature:**

	svmbir.auto_num_row( 
		sino
		delta_channel,
		delta_pixel
	) 

Computes the automatic value of ``n_row``, the number of rows in the reconstructed image volume.

**Parameters:**

 * ``sino``: 3D numpy array of sinogram data organized with shape ``[num_view,num_slice,num_channel]``.

 * ``delta_channel``: Scalar value of detector channel spacing in ALU.

 * ``delta_pixel``: Scalar value of the spacing between image pixels in the 2D slice plane in ALU.

**Returns:**

 * ``num_row``: Automatic number of rows.

#What it does:

This function computes the automatic value used for the number of rows in an image, ``num_row`` using the following formula:

	num_channel = sino.shape[2]
	num_row = numpy.ceil( num_channel * (delta_channel/delta_xy) )

#Example Usage:



