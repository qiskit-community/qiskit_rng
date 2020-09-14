# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# (C) Copyright CQC 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the Programs
# directory of this source or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
==============================
Qiskit RNG (:mod:`qiskit_rng`)
==============================

.. currentmodule:: qiskit_rng

Modules representing Qiskit Random Number Generator.

Classes
=========

.. autosummary::
    :toctree: stubs/

    Generator
    GeneratorJob
    GeneratorResult

Functions
=========
.. autosummary::
    :toctree: stubs/

    generate_wsr
"""

from .generator import Generator
from .generator_job import GeneratorJob
from .generator_result import GeneratorResult
from .utils import generate_wsr
