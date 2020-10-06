=============
Usage
=============

Workflow
--------

The current workflow has three parts:

1. Instantiate a :class:`qiskit_rng.Generator` from a specified IBM Quantum backend:

   .. code-block:: python

      from qiskit import IBMQ
      from qiskit_rng import Generator

      IBMQ.load_account()
      rng_provider = IBMQ.get_provider(hub='qrng')
      backend = rng_provider.backends.ibmq_ourence

      generator = Generator(backend=backend)

2. Sample a given number of "raw" bits using the target backend:

   .. code-block:: python

      output = generator.sample(num_raw_bits=1024).block_until_ready()

3. Extract high quality random numbers from the generator output:

   .. code-block:: python

      random_bits = output.extract(rng_provider)

   If you want to examine the final parameters passed to the extractor, you can use::

   .. code-block:: python

      extractor = rng_provider.random.cqc_extractor
      extractor_params = result.get_cqc_extractor_params()
      random_bits = extractor.run(*extractor_params)


Extractor Parameters
--------------------

* rate_sv: The assumption on the initial randomness rate of the used Weak Source of Randomness (WSR)
  as a Santha-Vazirani source. Effectively epsilon_sec / number of bits from the WSR
  (in a rate format).

* expected_correlator: The expected Mermin correlator value.
  :data:`qiskit_rng.constants.EXPECTED_CORRELATOR`
  contains known values for certain backends, which are calculated from long test samples and
  provide higher security (but lower generate rate). If set to ``None``, the observed value
  from the sampling output is used.

* epsilon_sec: A (small) security parameter defining the distance to uniform of the final bit
  string. When performing privacy amplification as well, epsilon is the distance to a perfectly
  uniform and private string.

* quantum_proof: Set to ``True`` for quantum-proof extraction in the Markov model (most secure) and
  to ``False`` for classical-proof extraction in the standard model (higher rates but lower
  security). This should be set to ``True`` for security against potential quantum adversaries.
  Note that setting ``quantum_proof`` to ``True`` reduces the generation rates considerably.

* trusted_backend: Set to ``True`` if the backend used for sampling is trusted and the interaction
  is made using a secure channel.

* privacy: Set to ``True`` to also perform privacy amplification and to ``False`` if the initial
  WSR is assumed private already. If set to ``True``, the final output is provably both private and
  unbiased. If set to ``False``, the final output is provably unbiased.


Use Case Examples and Suggested Parameters
------------------------------------------

In this section, we list different possible set of parameters for specific use cases and have
included only the ones that have a reasonable runtime on a real backend. The final output bit string
is certified quantum, random and private (if selected).

For all the use cases below, we recommend a `num_raw_bits` value of at least 30 million (`3e7`)
to the :meth:`qiskit_rng.Generator.sample()` method.

1. Random numbers for mathematical simulation or non-adversarial

   When there is no adversary or privacy concern, you can run with the minimum security parameters
   that allow the highest generation rate:

   * rate_sv=0.95
   * expected_correlator=None
   * epsilon_sec=1e-30
   * quantum_proof=False
   * trusted_backend=True
   * privacy=False

2. A good trade-off: certified quantum randomness

   We recommend this set of parameter which offers good security but which also runs efficiently:

   * rate_sv=0.95
   * expected_correlator=None
   * epsilon_sec=1e-30
   * quantum_proof=True
   * trusted_backend=True
   * privacy=False

3. A good trade-off: certified quantum randomness with privacy amplification

   This option is only available if the backend is trusted. We recommend this set of parameters:

   * rate_sv=0.95
   * expected_correlator=None
   * epsilon_sec=1e-30
   * quantum_proof=True
   * trusted_backend=True
   * privacy=True

4. Towards cryptographic use: certified quantum randomness using a untrusted backend:

   In this case, privacy amplification cannot be performed, and previously profiled correlator value
   should be used. We recommend this set of parameters:

   * rate_sv=0.95
   * expected_correlator=EXPECTED_CORRELATOR.xxx
   * epsilon_sec=1e-30
   * quantum_proof=True
   * trusted_backend=False
   * privacy=False

5. Towards cryptographic use: certified quantum randomness and privacy with a trusted backend

   This is the most stringent set of parameters in the possible presence of a quantum adversary.
   We recommend this set of parameters:

   * rate_sv=0.95
   * expected_correlator=EXPECTED_CORRELATOR.xxx
   * epsilon_sec=1e-30
   * quantum_proof=True
   * trusted_backend=True
   * privacy=True
