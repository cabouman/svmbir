===========
Quick Start
===========

A reconstruction is one call.  With a sinogram as a numpy array of shape
``(views, slices, channels)`` and the view angles in radians::

    import svmbir
    recon = svmbir.recon(sino, angles)

The result is a numpy array of shape ``(slices, rows, columns)``.

A complete example
------------------

This script makes a phantom, projects it, reconstructs from the projections,
and prints the error.  It runs in a few seconds on a laptop::

    import numpy as np
    import svmbir

    num_rows, num_cols, num_slices, num_views = 256, 256, 8, 144
    angles = np.linspace(0, np.pi, num_views, endpoint=False)

    phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows, num_cols, num_slices)
    sino = svmbir.project(phantom, angles, num_cols)
    recon = svmbir.recon(sino, angles)

    print('NRMSE:', svmbir.phantom.nrmse(recon, phantom))

The demo scripts in the repository (see :ref:`ExamplesDocs`) extend this to
fan beam, weighted data, multi-resolution, and proximal map reconstruction.

Your own data
-------------

- **Sinogram.**  A 3D numpy array in ``(views, slices, channels)`` order.
  Each slice is perpendicular to the rotation axis.  For transmission CT,
  normalize the raw photon counts by an air scan and take the negative log
  of the ratio before reconstruction.
- **Angles.**  A 1D numpy array with the rotation angle of each view in
  radians.  If the views were not collected in increasing angle order,
  sort them first with :func:`svmbir.sino_sort`; reconstruction is much
  slower on unsorted views.
- **Geometry.**  The default is parallel beam.  For fan beam, pass
  ``geometry='fan-curved'`` or ``geometry='fan-flat'`` together with
  ``dist_source_detector`` and ``magnification`` (see :ref:`OverviewDocs`).
- **Units.**  Distances are in arbitrary length units (ALU), where one ALU is
  the detector channel spacing by default (see :ref:`OverviewDocs`).

Tuning
------

The parameters most users change are:

- ``sharpness``: larger values give sharper images with more noise; the
  default is 0.
- ``snr_db``: the assumed signal-to-noise ratio of the data in dB; the
  default is 30.
- ``weight_type``: ``'unweighted'``, ``'transmission'``,
  ``'transmission_root'``, or ``'emission'`` (see :ref:`TheoryDocs`).
- ``positivity``: whether the reconstruction is constrained to be
  non-negative; the default is True.

All parameters are described in :ref:`APIDocs`.
