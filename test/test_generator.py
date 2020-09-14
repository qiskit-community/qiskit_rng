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

"""Test for the generator."""

from unittest import TestCase, mock
import os

from qiskit.test.mock.backends import FakeValencia
from qiskit_rng import Generator, GeneratorJob, GeneratorResult


class TestGenerator(TestCase):
    """Test random number generator."""

    def test_sample_basic(self):
        """Test basic sampling."""
        generator = Generator(FakeValencia())
        job = generator.sample(num_raw_bits=100)
        self.assertIsInstance(job, GeneratorJob)
        result = job.block_until_ready()
        self.assertIsInstance(result, GeneratorResult)

    def test_custom_wsr(self):
        """Test using custom wsr generator."""
        def _wsr_gen(num_bits):
            nonlocal gen_wsr
            gen_wsr = [1]*num_bits
            return gen_wsr

        gen_wsr = None
        generator = Generator(backend=FakeValencia(), wsr_generator=_wsr_gen)
        job = generator.sample(num_raw_bits=100)
        self.assertEqual(job.initial_wsr, gen_wsr)

    def test_save_local(self):
        """Test saving data locally."""
        generator = Generator(FakeValencia(), save_local=True)
        job = generator.sample(num_raw_bits=100)
        # Need to manually save since the backend is not an IBMQBackend.
        generator._save_local(100, job.wsr, job.job, job.shots)
        saved_fn = None
        file_prefix = Generator._file_prefix + '_'
        for entry in os.listdir():
            if entry.startswith(file_prefix):
                saved_fn = entry
                break
        self.assertTrue(saved_fn, "No saved file found.")
        job.saved_fn = saved_fn
        r_job = Generator.recover(saved_fn, mock.MagicMock())
        job.block_until_ready()
        try:
            self.assertFalse(any(fn.startswith(file_prefix) for fn in os.listdir()))
        except AssertionError:
            os.remove(saved_fn)
            raise
        self.assertEqual(r_job.wsr, job.wsr)
        self.assertEqual(r_job.shots, job.shots)

    def test_num_circs_shots(self):
        """Test the number of circuits and shots generated."""
        backend = FakeValencia()
        generator = Generator(backend)
        max_experiments = 5
        max_shots = 10
        backend._configuration.max_experiments = max_experiments
        backend._configuration.max_shots = max_shots
        sub_tests = [1, 3*max_shots, 3*max_shots+1, 3*max_shots-1,
                     3*max_shots*2, 3*max_shots*2+1, 3*max_shots*max_experiments-1]
        for num_raw_bits in sub_tests:
            with self.subTest(num_raw_bits=num_raw_bits):
                result = generator.sample(num_raw_bits=num_raw_bits).block_until_ready()
                self.assertGreaterEqual(len(result.raw_bits), num_raw_bits)
