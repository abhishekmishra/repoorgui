========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        |
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/repoorgui/badge/?style=flat
    :target: https://repoorgui.readthedocs.io/
    :alt: Documentation Status

.. |commits-since| image:: https://img.shields.io/github/commits-since/abhishekmishra/repoorgui/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/abhishekmishra/repoorgui/compare/v0.0.1...main



.. end-badges

GIT Repo Organizer

* Free software: MIT license

Installation
============

::

    pip install repoorgui

You can also install the in-development version with::

    pip install https://github.com/abhishekmishra/repoorgui/archive/main.zip


Documentation
=============


https://repoorgui.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
