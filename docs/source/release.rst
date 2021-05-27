=======================
Preparing a new release
=======================

Code changes that are to be included in the next release should be merged into
the ``prerelease`` branch.
The following lists the procedure for creating a new release.

NOTE Only a few dedicated maintainers should do this.

1. Check out the ``prerelease`` branch and ensure the submodule is current.

	| ``git checkout prerelease``
	| ``git submodule update``

2. Verify the new version number in ``setup.py`` is accurate. If not, change and commit.

3. Run `unit tests <pytest.html>`_ for all supported compilers and platforms.

4. Merge the ``prerelease`` branch into ``master`` (via pull request).

5. Create a new release tag for the new master commit.

	| ``git checkout master``
	| ``git pull origin master``
	| ``git tag v<ver_no> -a -m "version <ver_no>"   # ex. git tag v0.2.10 -a -m "version 0.2.10"``
	| ``git push origin <tagname>   # ex. git push origin v0.2.10``

6. Review documentation `locally <docs.html>`_.

7. Build/upload package to `TestPyPI <pypi.html>`_ and test installation.

8. Build/upload package to `PyPI <pypi.html>`_ and test installation.

