# ``svmbir.calc_weights``

**Signature:**

	svmbir.calc_weights( 
		sino, 
		weights=None,
		weight_type="unweighted",
	) 

Computes the weights used in reconstruction. 

**Parameters:**

 * ``sino``: 3D numpy array of sinogram data organized with ``sino[slice,channel,view]``.

 * ``weights``: [Default=None] 3D numpy array of weights with same shape as ``sino``. 

 * ``weight_type``: [Default=0] Type of noise model used for data. 

The parameters ``weights`` and ``weight_type`` should be the same values as used in svmbir reconstruction.
	
**Returns:**

 * ``partial_weights``: Calculated values of partial_weight parameter.

#What it does:

This function computes the partial weights using the values of the ``weights`` and ``weight_type`` parameters as shown below:

	If weights=None {
		If weight_type="unweighted" => weights = np.ones_like(sino)
		If weight_type="transmission" => weights = numpy.exp(-sino)
		If weight_type="transmission_root" => weights = numpy.exp(-sino/2)
		If weight_type="emmission" => weights = 1/(sino + 0.1)
	}

#Example Usage:
