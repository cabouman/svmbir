=======================
Preparing a new release
=======================

Code changes that are to be included in the next release should be merged into
the ``prerelease`` branch.
The following lists the procedure for creating a new release.

NOTE Only a few dedicated maintainers should do this.

1. Check out the ``prerelease`` branch and ensure the submodule is current::

    $ git checkout prerelease
    $ git submodule update

2. Make sure that the demo.zip file is up-to-date. If not, then run the script ``dev_scripts/zip_demo_folder.sh`` and commit.

3. Verify the new version number in ``svmbir/__init__.py`` is accurate. If not, change and commit.

4. Run `unit tests <pytest.html>`_ for all supported compilers and platforms.

5. Merge the ``prerelease`` branch into ``master`` (via pull request).

6. Create a new release tag for the new master commit::

    $ git checkout master
    $ git pull origin master
    $ git tag v<ver_no> -a -m "version <ver_no>"   # ex. git tag v0.2.10 -a -m "version 0.2.10"
    $ git push origin <tagname>   # ex. git push origin v0.2.10

7. Review documentation `locally <docs.html>`_.

8. Build/upload package to `TestPyPI <pypi.html>`_ and test installation.

9. Build/upload package to `PyPI <pypi.html>`_ and test installation.

