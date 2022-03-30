==================
Clean installation
==================

A number of bash scripts provided in the directory ``dev_scripts`` for cleaning and reinstalling the ``svmbir`` environment.

In order to completely remove ``svmbir``,
``cd`` into ``dev_scripts`` and run the command::

    $ source clean_svmbir.sh

In order to install ``svmbir`` along with requirements for ``svmbir``, demos, and docs,
``cd`` into ``dev_scripts`` and run the command::

    $ source install_svmbir.sh

In order to install documentation that can be viewed from ``svmbir/docs/build/index.html``,
``cd`` into ``dev_scripts`` and run the command::

    $ source install_docs.sh

In order to destroy the conda environement named ``svmbir`` and then recreate and activate it,
``cd`` into ``dev_scripts`` and run the command::

    $ source install_conda_environment.sh

In order to destroy and clean everything, and then recreate the conda environment and reinstall ``svmbir`` and its documentation
``cd`` into ``dev_scripts`` and run the command::

    $ source clean_install_conda_svmbir_docs.sh

**Be careful with these last two commands** because they will destroy the conda environment named ``svmbir``.
