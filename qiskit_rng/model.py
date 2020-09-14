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

"""Module for different object models."""

from typing import NamedTuple, Callable


class CQCExtractorParams(NamedTuple):
    """Named tuple used to hold parameters to a CQC extractor."""
    ext1_input_num_bits: int
    ext1_output_num_bits: int
    ext1_raw_bytes: bytes
    ext1_wsr_bytes: bytes
    ext2_seed_num_bits: int
    ext2_wsr_multiplier: int
    ext2_wsr_generator: Callable
