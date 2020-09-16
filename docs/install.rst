=============
Installation
=============

Overview
--------

Installation of ``qiskit_rng`` has two pieces.  First, this module itself
that contains the RNG number generation.  And second, a subset of the 
`Qiskit <https://qiskit.org/>`_ SDK that
constructs quantum circuits, and makes the appropriate API calls to execute
those circuits and later call the extractor API.  Both of these pieces
are installed with a single command.


Install
-------

Installation of ``qiskit_rng`` is a simple call tp PyPI:

.. code-block:: bash

   pip install qiskit_rng
