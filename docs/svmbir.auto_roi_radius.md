# ``svmbir.auto_roi_radius``

**Signature:**

	svmbir.auto_roi_radius( 
		num_row=None,
		num_col=None,
		delta_pixel=1.0,
	) 

Computes the automatic value of ``roi_radius``, the region of interest radius to reconstruct.

**Parameters:**

 * ``num_row``: [Default=None] Integer number of rows in reconstructed image. If ``None``, automatically set by calling ``svmbir.auto_n_row``.

 * ``num_col``: [Default=None] Integer number of columns in reconstructed image. If ``None``, automatically set by calling ``svmbir.auto_n_col``.

 * ``delta_pixel``: [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in ALU.
	
**Returns:**

 * ``roi_radius``: Automatic value of the region-of-interest radius.

#What it does:

This function computes an automatic value of the region-of-interest radius given by:

	roi_radius = delta_xy * max(num_row,num_col)

#Example Usage:



