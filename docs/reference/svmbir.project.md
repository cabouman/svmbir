# ``svmbir.project``

**Signature:**

	svmbir.project( 
		num_channel, 
		num_slice,
		angles,
		image, 

		delta_channel=1.0, 
		center_offset=0.0,

		delta_pixel=1.0, 
		roi_radius=None,

		num_threads=1, 	
		delete_temps=True
		svmbir_lib_path=`~/.cache/svmbir_lib`
	) 

Computes the parallel beam sinogram of a 3D numpy array ``image`` that represents the volumetric image. 

**Required Parameters:**

 * ``num_channel``: Integer number of sinogram channels.

 * ``num_view``: Integer number of sinogram vews.

 * ``angles``: 1D numpy array of view angles in radians. 

 * ``image``: 3D numpy array of image being forward projected. 

The 1D array is organized so that ``angles[k]`` is the angle in radians for view ``k``. The ``image`` is a 3D image with a shape of ``[num_slices,num_row,num_col]`` where ``num_slices`` is the number of sinogram slices. The ``image`` should be 0 outside the ROI as defined by ``roi_radius``.

**Sinogram Parameters:**

 * ``delta_channel``: [Default=1.0] Scalar value of detector channel spacing in ALU.

 * ``center_offset``: [Default=0.0] Scalar value of offset from center-of-rotation.

The offset in the center of rotation in units of number of detector channels from the center of detector. This value can be fractional.

**Image Parameters:**

 * ``delta_pixel``: [Default=1.0] Scalar value of the spacing between image pixels in the 2D slice plane in ALU.

 * ``roi_radius``: [Default=None] Scalar value of radius of reconstruction in ALU. If ``None``, automatically set by calling ``svmbir.auto_roi_radius``.
 
The angle=0 corresponds to integration along the $x$ coordinate, i.e., along rows of the reconstruction. Pixels outside the radius ``roi_radius`` in the $(x,y)$ plane are disregarded in forward projection. The automatically set size of ``roi_radius`` is choosen so that it inscribes the largest axis of the recon image with a shape ``[num_slices,num_row,num_col]``.

**Additional Parameters:**

 * ``num_threads``: [Default=1] Number of compute threads requested when executed.

 * ``delete_temps``: [Default=True] Delete temporary files used in computation.

 * ``svmbir_lib_path``: [Default=`~/.cache/svmbir_lib`] String containing path to directory containing library of forward projection matrices and temp file.

**Returns:**

 * ``sino``: 3D numpy array containing sinogram with shape ``[num_view,num_slice,num_channel]``. 
   

#Example Usage:

