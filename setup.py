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

import os

from setuptools import setup, find_packages

REQUIREMENTS = [
    "qiskit-ibmq-provider>=0.10",
    "qiskit-terra>=0.16.2"
]

# Read long description from README.
README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.md')
with open(README_PATH) as readme_file:
    README = readme_file.read()

version_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'qiskit_rng',
    'VERSION.txt'))

with open(version_path, 'r') as fd:
    version_str = fd.read().rstrip()

setup(
    name="qiskit_rng",
    version=version_str,
    description="Qiskit Random Number Generator.",
    long_description=README,
    long_description_content_type='text/markdown',
    url="https://github.com/qiskit-community/qiskit_rng",
    author="Qiskit Development Team",
    author_email="hello@qiskit.org",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    keywords="qiskit quantum cqc qrng",
    packages=find_packages(exclude=['test*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    python_requires=">=3.6",
    project_urls={
        "Bug Tracker": "https://github.com/qiskit-community/qiskit_rng/issues",
        "Documentation": "https://qiskit-rng.readthedocs.io",
        "Source Code": "https://github.com/qiskit-community/qiskit_rng",
    },
    zip_safe=False
)
