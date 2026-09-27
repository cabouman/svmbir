.. svmbir documentation master file.

SVMBIR: Fast parallel-beam MBIR reconstruction
==============================================

**svmbir** is a Python package for Model Based Iterative Reconstruction (MBIR) of
parallel-beam and fan-beam tomography data.  It wraps the super-voxel C code
`sv-mbirct <https://github.com/HPImaging/sv-mbirct>`_ :cite:`wang2016high` :cite:`wang2017massively`,
which runs on multi-core CPUs.

**Key features:**

* Fast reconstruction: the super-voxel algorithm is 100 to 1000 times faster than conventional MBIR code on a CPU.
* Parallel-beam and fan-beam geometries (see :ref:`OverviewDocs`).
* Bayesian reconstruction with a qGGMRF prior, well suited to sparse-view and noisy data.
* A proximal map interface for Plug-and-Play priors :cite:`venkatakrishnan2013plug` :cite:`sreehari2016plug`.
* Automatic parameter selection, with a small set of parameters for fine-tuning.
* A function interface of a few calls: ``project``, ``backproject``, and ``recon``.

For GPU reconstruction, cone-beam and other geometries, and new development,
see `MBIRTorch <https://mbirtorch.readthedocs.io>`_, the current package in the
`OpenMBIR <https://github.com/cabouman/OpenMBIR-Resources>`_ family.


.. grid:: 3
   :margin: 0
   :padding: 0
   :gutter: 0

   .. grid-item-card:: Simple API
      :columns: 12 6 6 4
      :class-card: sd-border-0
      :shadow: None

      A reconstruction is one function call on a sinogram and its view angles.

   .. grid-item-card:: Fast on a CPU
      :columns: 12 6 6 4
      :class-card: sd-border-0
      :shadow: None

      Super-voxel coordinate descent uses every core and the cache well.

   .. grid-item-card:: Plug-and-Play priors
      :columns: 12 6 6 4
      :class-card: sd-border-0
      :shadow: None

      The proximal map interface accepts any denoiser as the prior.


.. grid:: 3

    .. grid-item-card:: :material-regular:`rocket_launch;2em` Getting Started
      :class-card: getting-started
      :columns: 12 6 6 4
      :link: quick_start
      :link-type: doc

    .. grid-item-card:: :material-regular:`library_books;2em` User Guides
      :class-card: user-guides
      :columns: 12 6 6 4
      :link: install
      :link-type: doc

    .. grid-item-card:: :material-regular:`laptop_chromebook;2em` Developer Docs
      :class-card: developer-docs
      :columns: 12 6 6 4
      :link: dev_maintenance
      :link-type: doc


.. toctree::
   :hidden:
   :maxdepth: 4
   :caption: Background

   overview
   quick_start
   theory
   credits

.. toctree::
   :hidden:
   :maxdepth: 4
   :caption: User Guide

   install
   api
   examples

.. toctree::
   :hidden:
   :maxdepth: 4
   :caption: Developer Guide

   dev_maintenance
