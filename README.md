# Qiskit Random Number Generation

[![License](https://img.shields.io/github/license/Qiskit/qiskit-ignis.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://github.com/qiskit-community/qiskit_rng/workflows/Tests/badge.svg?style=popout-square)](https://github.com/qiskit-community/qiskit_rng/actions)
[![](https://img.shields.io/github/release/qiskit-community/qiskit_rng.svg?style=popout-square)](https://github.com/qiskit-community/qiskit_rng/releases)
[![](https://img.shields.io/pypi/dm/qiskit_rng.svg?style=popout-square)](https://pypi.org/project/qiskit_rng/)

Qiskit is an open-source framework for working with noisy intermediate-scale
quantum computers (NISQ) at the level of pulses, circuits, and algorithms.

This project contains support for Random Number Generation using [Qiskit] 
and [IBM Quantum Experience] backends. The 
resulting raw numbers can then be passed to [Cambridge Quantum Computing] (CQC)
randomness extractors to get higher-quality random numbers.

## Installation

You can install the project using pip:

```bash
pip install qiskit_rng
```

PIP will handle all python dependencies automatically, and you will always
install the latest (and well-tested) version.


## Usage

### Setting up the IBM Quantum Provider

You will need setup your IBM Quantum Experience account and provider in order to 
access IBM Quantum backends. See [qiskit-ibmq-provider](https://github.com/Qiskit/qiskit-ibmq-provider)
for more details.

### Generating random numbers using an IBM Quantum backend

To generate random numbers using an IBM Quantum backend:

```python
from qiskit import IBMQ
from qiskit_rng import Generator

IBMQ.load_account()
rng_provider = IBMQ.get_provider(hub='MY_HUB', group='MY_GROUP', project='MY_PROJECT')
backend = rng_provider.backends.ibmq_ourence

generator = Generator(backend=backend)
output = generator.sample(num_raw_bits=int(1024), fast_path=True).block_until_ready()
print(output.mermin_correlator)
```

The `output` you get back contains useful information such as the 
Weak Source of Randomness (`result.wsr`) used to generate the circuits, the resulting bits 
(`result.raw_bits`), and the Mermin correlator value (`result.mermin_correlator`). 


### Using CQC extractors to get highly random output
 
If you have access to the CQC extractors, you can feed the outputs from the previous
step to obtain higher quality random numbers:

```python
print(rng_provider.random.services())  # Show a list of random services you have access to.
extractor = rng_provider.random.cqc_extractor
extractor_params = result.get_cqc_extractor_params()
random_bits = extractor.run(*extractor_params)
```

The code above uses the default parameter values, but the extractor is highly 
configurable. See documentation for some use case examples and parameter suggestions.

## License

[Apache License 2.0].


[Qiskit]: https://qiskit.org
[IBM Quantum Experience]: https://quantum-computing.ibm.com
[Cambridge Quantum Computing]: https://cambridgequantum.com
[Apache License 2.0]: https://github.com/qiskit-community/qiskit_rng/blob/master/LICENSE.txt
