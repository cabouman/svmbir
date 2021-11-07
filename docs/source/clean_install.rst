==================
Clean installation
==================

There are some bash scripts provided in the directory ``dev_scripts`` for cleaning and reinstalling the ``svmbir`` environment.

In order to completely remove ``svmbir``, you can run the command:

``source dev_scripts/clean_svmbir.sh``

In order to destroy and then recreate your conda and ``svmbir`` environments, you can run the command:

``source dev_scripts/clean_install_with_docs.sh``

**Be careful with this command** because it will distroy the conda environment named ``svmbir``.
It also will reinstall all requirements for ``svmbir``, demos, and documentation, and it will rebuild the documentation.
If you would prefer to do a subset of these things, you can run individual commands from the script.
