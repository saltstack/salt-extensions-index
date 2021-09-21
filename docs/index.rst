The Salt extensions listed in this index are collected by searching `PyPi`_ for packages
starting with ``salt-ext-``, ``saltext-`` or ``saltext.`` in their name, or, preferably,
by having ``salt-extension`` in the package's `keywords`_ metadata entry:

An effort is made to automatically test these packages against the latest 3 major releases
of salt. For this to happen, the package:

* Must use `nox`_ to run it's test suite
* Must provide a source distribution which includes a ``noxfile.py``
* The ``noxfile.py`` must implement a ``tests-3`` session
* The ``noxfile.py`` must check the environment for a ``SALT_REQUIREMENT`` keyword which should be installed into the `nox`_ session. (Example ``SALT_REQUIREMENT=salt==3004.0``)

.. _PyPi: https://pypi.org/
.. _keywords: https://www.python.org/dev/peps/pep-0314/#keywords-optional
.. _nox: https://github.com/theacodes/nox

.. warning::

   This extensions listing is still in it's **proof of concept** phase.
   The Salt Project team is evaluating this index and investigating how to improve it in order to better serve the Salt Project Community
..
  Auto generated content starts here

------------
