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

"""Generator job."""

import os
import logging
from typing import List, Union, Optional

from qiskit.providers.basejob import BaseJob
from qiskit.providers.ibmq.managed.ibmqjobmanager import ManagedJobSet
from qiskit.result.result import Result

from .generator_result import GeneratorResult

logger = logging.getLogger(__name__)


class GeneratorJob:
    """Representation of a job that executes on a backend that can generate random numbers."""

    def __init__(
            self,
            initial_wsr: List[int],
            wsr: List[List],
            job: Union[BaseJob, ManagedJobSet],
            shots: int,
            saved_fn: Optional[str] = None
    ) -> None:
        """GeneratorJob constructor.

        Args:
            initial_wsr: Initial raw WSRs.
            wsr: Processed WSRs used to generate circuits.
            job: Circuit job(s).
            shots: Number of shots.
            saved_fn: Name of the file used to save context information.
        """
        self.initial_wsr = initial_wsr
        self.wsr = wsr
        self.job = job
        self.backend = job._backend
        self.shots = shots

        self.raw_bits_list = None
        self.formatted_wsr = None
        self.saved_fn = saved_fn

    def block_until_ready(self) -> GeneratorResult:
        """Block until result data is ready.

        Returns:
            A :class:`GeneratorResult` instance that contains information
            needed to run the extractor.
        """
        logger.info("Waiting for jobs to finish.")
        if isinstance(self.job, ManagedJobSet):
            js_results = self.job.results()
            job_result = js_results.combine_results()
        else:
            job_result = self.job.result()
        logger.info("All jobs finished, transforming job results.")

        self.raw_bits_list = self._ibmq_result_transform(job_result)
        self._format_wsr()
        if self.saved_fn:
            try:
                os.remove(self.saved_fn)
            except Exception:   # pylint: disable=broad-except
                logger.warning("Unable to delete file %s", self.saved_fn)
        return GeneratorResult(wsr=self.formatted_wsr, raw_bits_list=self.raw_bits_list)

    def _format_wsr(self):
        """Format the wsr.

        Convert the WSR to the format of
        ``[wsr1, wsr1, ... wsr1_n, wsr2, wsr2, ...]``
        where ``n`` is the number of shots. Each wsr is a list of 3 bits.
        """
        if not self.formatted_wsr:
            # Convert [wsr1, wsr2] to [wsr1, wsr1, ...wsr1_n, wsr2, wsr2, ...],
            # where n is the number of shots. Each wsr is a list of 3 bits.
            self.formatted_wsr = \
                [wsr_set[:] for wsr_set in self.wsr for _ in range(self.shots)]

    def _ibmq_result_transform(self, result: Result) -> List[List]:
        """Transform IBMQ result data into the proper format.

        Args:
            result: Job result.

        Returns:
            Job results in the format of
            ``[circ1_shot1, circ1_shot2, ..., circ2_shot1, circ2_shot2, ...]``.
            Each circn_shotn is a list of 3 bits.
        """
        all_results = []
        for i in range(len(result.results)):
            # Convert ['101', '110', ...] to [[1, 0, 1], [0, 1, 1], ...]
            circ_mem = result.get_memory(i)  # ['101', '110', ...]
            for shot_mem in circ_mem:
                shot_list = [int(mem) for mem in shot_mem]
                shot_list.reverse()
                all_results.append(shot_list)

        return all_results
