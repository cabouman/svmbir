# ``svmbir.auto_sigma_y``

**Signature:**

	svmbir.auto_sigma_y( 
		sino, 
		snr_db=30.0,
		weights=None,
		weight_type="unweighted",
	) 

Computes the automatic value of the regularization parameter ``sigma_y`` for use in MBIR reconstruction. 

**Parameters:**

 * ``sino``: 3D numpy array of sinogram data organized with ``sino[slice,channel,view]``.

 * ``snr_db``: [Default=30.0] Scalar value that controls assumed signal-to-noise ratio of the data in dB.

 * ``weights``: [Default=None] 3D numpy array of weights with same shape as ``sino``. 

 * ``weight_type``: [Default=0] Type of noise model used for data. Can be set to the values ``unweighted``, ``transmission``, ``transmission_root``, and ``emission``. 

The parameters ``weights`` and ``weight_type`` should be the same values as used in svmbir reconstruction.
	
**Returns:**

 * ``sigma_y``: Automatic values of regularization parameter.

#What it does:

This function computes a automatic value for the regularization parameter ``sigma_y`` is computed using the formula:

 	weights = svmbir.calc_weights(sino=sino,weights=weights,weight_type=weight_type)
	signal_rms = numpy.mean(partial_weights * sino**2)**0.5
	rel_noise_std = (-snr_db/20)**10
	sigma_y = rel_noise_std * signal_rms

So for the default SNR of 30dB using ``weight_type=0``, the resulting parameter is ``sigma_y=0.0316``, which means an assumed noise standard deviation of approxmiately 3%. If the data has higher SNR, then the value of ``snr_db`` can be increased. 

#Example Usage:



