The svmbir API reference
========================

* svmbir_ includes functions for tomographic projection and reconstruction
  as well as some helper functions.
* phantom_ includes functions to generate 2D and 3D phantoms and an nrmse utility.

.. _svmbir:

svmbir
------
.. automodule:: svmbir
   :members: 
   :undoc-members:
   :show-inheritance:

   .. rubric:: **Functions:**

   .. autosummary::

      auto_sigma_x
      auto_sigma_y
      calc_weights
      project
      recon

-------------------

.. _phantom:

svmbir.phantom
--------------
.. automodule:: svmbir.phantom
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: **Functions:**

   .. autosummary::

      gen_microscopy_sample
      gen_shepp_logan
      gen_shepp_logan_3d
      nrmse
