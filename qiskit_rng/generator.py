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

"""Module for random number generator."""

import logging
import pickle
import uuid
import os
from itertools import product
from typing import List, Tuple, Callable, Optional, Any, Union

from qiskit import QuantumCircuit, transpile
from qiskit.providers.basebackend import BaseBackend
from qiskit.providers.basejob import BaseJob
from qiskit.providers.ibmq.ibmqbackend import IBMQBackend
from qiskit.providers.ibmq.managed.ibmqjobmanager import IBMQJobManager, ManagedJobSet
from qiskit.providers.ibmq.accountprovider import AccountProvider

from .generator_job import GeneratorJob
from .utils import generate_wsr

try:
    from qiskit.providers.backend import Backend
    HAS_V2_BACKEND = True
except ImportError:
    HAS_V2_BACKEND = False

logger = logging.getLogger(__name__)


class Generator:
    """Class for generating random numbers.

    You can use the :meth:`sample` method to run quantum circuits on a backend
    to generate random bits. When the circuit jobs finish and their results
    processed, you can examine the generated random bits as well as the
    bell values. An example of this flow::

        from qiskit import IBMQ
        from qiskit_rng import Generator

        provider = IBMQ.load_account()
        generator = Generator(backend=provider.backends.ibmq_valencia)
        output = generator.sample(num_raw_bits=1024).block_until_ready()
        print("Mermin correlator value is {}".format(output.mermin_correlator))
        print("first 8 raw bits are {}".format(output.raw_bits[:8]))

    Note that due to the way the circuits are constructed and executed, the resulting
    size of ``raw_bits`` might be slightly larger than the input ``num_raw_bits``.

    The bits generated by the :meth:`sample` method are only weakly random. You
    will need to apply a randomness extractor to this output in order to obtain
    a more uniformly distributed string of random bits.
    """

    _file_prefix = "qiskit_rng"
    _job_tag = 'qiskit_rng'

    def __init__(
            self,
            backend: BaseBackend,
            wsr_generator: Optional[Callable] = None,
            noise_model: Any = None,
            save_local: bool = False
    ) -> None:
        """Generator constructor.

        Args:
            backend: Backend to use for generating random numbers.
            wsr_generator: Function used to generate WSR. It must take the
                number of bits as the input and a list of random bits (0s and 1s)
                as the output. If ``None``, :func:`qiskit_rng.generate_wsr` is used.
            noise_model: Noise model to use. Only applicable if `backend` is a
                simulator.
            save_local: If ``True``, the generated WSR and other metadata is
                saved into a pickle file in the local directory. The file can
                be used to recover and resume a sampling if needed.
                The file name will be in the format of
                ``qiskit_rng_<backend>_<num_raw_bits>_<id>``.
                The file will be deleted automatically when the corresponding
                :meth:`GeneratorJob.block_until_ready()` method is invoked.
                Only supported if `backend` is an ``IBMQBackend``.
        """
        self.backend = backend
        self.job_manager = IBMQJobManager()
        self.wsr_generator = wsr_generator or generate_wsr
        self.noise_model = noise_model
        self.save_local = save_local

    def sample(
            self,
            num_raw_bits: int
    ) -> GeneratorJob:
        """Use the target system to generate raw bit strings.

        Args:
            num_raw_bits: Number of raw bits to sample. Note that the raw
                bits are only weakly random and needs to go through extraction
                to generate highly random output.

        Returns:
            A :class:`GeneratorJob` instance that contains all the information
                needed to extract randomness.

        Raises:
            ValueError: If an input argument is invalid.
        """
        if not isinstance(self.backend, BaseBackend) and \
                (HAS_V2_BACKEND and not isinstance(self.backend, Backend)):
            raise ValueError("Backend needs to be a Qiskit `BaseBackend` or `Backend` instance.")

        max_shots = self.backend.configuration().max_shots
        num_raw_bits_qubit = int((num_raw_bits + 2)/3)
        if num_raw_bits_qubit <= max_shots:
            shots = num_raw_bits_qubit
            num_circuits = 1
        else:
            num_circuits = int((num_raw_bits_qubit + max_shots - 1)/max_shots)
            shots = int((num_raw_bits_qubit + num_circuits - 1)/num_circuits)

        logger.debug("Using %s circuits with %s shots each", num_circuits, shots)

        initial_wsr = self.wsr_generator(num_circuits * 3)

        wsr_bits = self._get_wsr(num_circuits, initial_wsr)
        circuits = self._generate_all_circuits(num_circuits, wsr_bits)

        job = self._run_circuits(circuits, shots)
        saved_fn = None
        if self.save_local and isinstance(self.backend, IBMQBackend):
            saved_fn = self._save_local(num_raw_bits, wsr_bits, job, shots)
        return GeneratorJob(
            initial_wsr=initial_wsr,
            wsr=wsr_bits,
            job=job,
            shots=shots,
            saved_fn=saved_fn
        )

    def _run_circuits(
            self,
            circuits: List[QuantumCircuit],
            shots: int
    ) -> Union[ManagedJobSet, BaseJob]:
        """Run circuits on a backend.

        Args:
            circuits: Circuits to run.
            shots: Number of shots.

        Returns:
            An IBMQ managed job set or a job.
        """
        transpiled = transpile(circuits, backend=self.backend, optimization_level=2)
        transpiled = [transpiled] if not isinstance(transpiled, list) else transpiled

        if isinstance(self.backend, IBMQBackend):
            job = self.job_manager.run(transpiled, backend=self.backend, shots=shots,
                                       job_tags=[self._job_tag], memory=True)
            logger.info("Jobs submitted to %s. Job set ID is %s.", self.backend, job.job_set_id())
        else:
            job = self.backend.run(circuits, shots=shots, noise_model=self.noise_model, memory=True)
            logger.info("Jobs submitted to %s. Job ID is %s.", self.backend, job.job_id())

        return job

    def _get_wsr(self, num_circuits: int, initial_wsr: List[int]) -> List:
        """Obtain the weak source of randomness bits used to generate circuits.

        Args:
            num_circuits: Number of circuits.
            initial_wsr: Raw WSR bits used to generate the output WSR.

        Returns:
            A list the size of `num_circuits`. Each element in the
                list is another list of 3 binary numbers.
                For example,
                [ [1, 0, 0], [0, 1, 1], [1, 1, 0], ...]
        """
        output_wsr = []
        for i in range(num_circuits):
            output_wsr.append(
                [int(initial_wsr[3*i]), int(initial_wsr[3*i+1]), int(initial_wsr[3*i+2])])

        return output_wsr

    def _generate_circuit(self, label: Tuple[int, int, int]) -> QuantumCircuit:
        """Generate a circuit based on the input label.

        The size of the input label determines the number of qubits.
        An ``sdg`` is added to the circuit for the qubit if the corresponding
        label value is a ``1``.

        Args:
            label: Label used to determine how the circuit is to be constructed.
                A tuple of 1s and 0s.

        Returns:
            Constructed circuit.
        """
        num_qubit = len(label)
        qc = QuantumCircuit(num_qubit, num_qubit)
        qc.h(0)
        for i in range(1, num_qubit):
            qc.cx(0, i)
        qc.s(0)
        qc.barrier()
        for i in range(num_qubit):
            if label[i] == 1:
                qc.sdg(i)
        for i in range(num_qubit):
            qc.h(i)
        qc.measure(qc.qregs[0], qc.cregs[0])
        return qc

    def _generate_all_circuits(self, num_circuits: int, wsr_bits: List) -> List[QuantumCircuit]:
        """Generate all circuits based on input WSR bits.

        Args:
            num_circuits: Number of circuits to generate.
            wsr_bits: WSR bits used to determine which circuits to use.

        Returns:
            A list of generated circuits.
        """
        # Generate 3-qubit circuits for each of the 8 permutations.
        num_qubits = 3
        labels = list(product([0, 1], repeat=num_qubits))

        # Generate base circuits.
        circuits = []
        for label in labels:
            circuits.append(self._generate_circuit(label))

        # Construct final circuits using input WSR bits.
        final_circuits = []
        for i in range(num_circuits):
            wsr_set = wsr_bits[i]    # Get the 3-bit value.
            final_circuits.append(circuits[labels.index(tuple(wsr_set))])

        return final_circuits

    def _save_local(
            self,
            num_raw_bits: int,
            wsr_bits: List,
            job: Union[ManagedJobSet, BaseJob],
            shots: int
    ) -> str:
        """Save context information for the sampling.

        Args:
            num_raw_bits: Number of raw bits requested.
            wsr_bits: WSR bits to save.
            job: Job whose ID is to be saved.
            shots: Number of shots.

        Returns:
            Name of the file with saved data.
        """
        file_prefix = "{}_{}_{}_".format(
            self._file_prefix, self.backend.name(), num_raw_bits)
        file_name = file_prefix + str(uuid.uuid4())[:4]
        while os.path.exists(file_name):
            file_name = file_prefix + str(uuid.uuid4())[:4]

        data = {"wsr": wsr_bits, "shots": shots}
        if isinstance(job, ManagedJobSet):
            data["job_id"] = job.job_set_id()
            data["job_type"] = "jobset"
        else:
            data["job_id"] = job.job_id()
            data["job_type"] = "job"
        with open(file_name, 'wb') as file:
            pickle.dump(data, file)
        return file_name

    @classmethod
    def recover(cls, file_name: str, provider: AccountProvider) -> GeneratorJob:
        """Recover a previously saved sampling run.

        Args:
            file_name: Name of the file containing saved context.
            provider: Provider used to do the sampling.

        Returns:
            Recovered output of the original :meth:`sample` call.
        """
        with open(file_name, 'rb') as file:
            data = pickle.load(file)
        job_id = data['job_id']
        job_type = data['job_type']
        if job_type == "jobset":
            job = IBMQJobManager().retrieve_job_set(job_id, provider)
        else:
            job = provider.backends.retrieve_job(job_id)

        return GeneratorJob(
            initial_wsr=[],
            wsr=data['wsr'],
            job=job,
            shots=data["shots"],
            saved_fn=file_name
        )
