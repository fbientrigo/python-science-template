Science Project
===============

This documentation is built from the same locked project environment used by verification.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api

Development contract
--------------------

``make verify`` is the canonical project gate. It builds the shared container, mounts the checkout read-only, and runs lint, tests, docs, and the smoke entry point in an ephemeral copy.
