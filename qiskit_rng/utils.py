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

"""Module for utility functions."""

import logging
from typing import List, Tuple
from math import sqrt, log2, floor

import numpy as np

logger = logging.getLogger(__name__)


def bell_value(
        wsr: List[List[int]],
        raw_bits: List[List[int]]
) -> Tuple[float, float, float]:
    """Calculate the bell values.

    Args:
        wsr: WSR used to calculate the raw bits.
        raw_bits: Random bits used to calculate the bell values.

    Returns:
        A tuple of Mermin losing probability, winning probability, and correlator.
    """
    losing_prob = 0
    for i in range(len(wsr)):   # pylint: disable=consider-using-enumerate
        wsr_sum = sum(wsr[i])
        raw_bits_sum = sum(raw_bits[i])
        if wsr_sum == 1 and raw_bits_sum % 2 == 1:
            losing_prob += 1
        elif wsr_sum == 3 and raw_bits_sum % 2 == 0:
            losing_prob += 1
    losing_prob = losing_prob / len(wsr)
    winning_prob = 1 - losing_prob
    correlator = 4-16*losing_prob

    return losing_prob, winning_prob, correlator


def get_extractor_bits(raw_bits: List[List[int]]) -> List[int]:
    """Return bits to be used by the extractor.

    Args:
        raw_bits: Input raw bits from sampling jobs.

    Returns:
        A list of bits that can be used by the extractor.
    """
    bits = []
    for bit_set in raw_bits:
        bits += bit_set[:2]
    return bits


def h_mins(bt_value: float, num_bits: int, rate_sv: float) -> float:
    """Calculate the minimum entropy for each bit.

    Args:
        bt_value: Bell value.
        num_bits: The 2/3 outcomes bits from each circuit.
        rate_sv: The assumption on the initial randomness rate of the WSR as a
         Santha-Vazirani source.

    Returns:
        Minimum entropy for each bit.
    """
    epsilon_sv = 2**(-rate_sv) - 1 / 2
    h_min_bt = -num_bits / 2 * log2(guessing_probability(bt_adjusting(bt_value, epsilon_sv)))
    rate_bt = h_min_bt / num_bits
    return rate_bt


def na_set(num_bits: int) -> int:
    """Ensure the number of runs falls within the correct set.

    This is to validate the inputs to the extractor and involves checking the
    primality of the input.

    Args:
        num_bits: Number to check is in the set.

    Returns:
        Updated number in the set.
    """
    if num_bits % 2 != 0:
        num_bits = num_bits - 1
    stop = False
    while not stop:
        stop = True
        while not prime_check(num_bits + 1):
            num_bits = num_bits - 2
        output = prime_factors(num_bits, True)
        prime_powers = output[1]
        primes = output[0]
        for i in range(len(prime_powers)):
            test = pow(2, int(num_bits / primes[i]), num_bits + 1)
            if test == 1:
                stop = False
        if not stop:
            num_bits = num_bits - 2
    return num_bits


def prime_check(num: int) -> bool:
    """Check whether the input number is a prime number.

    Args:
        num: Number to be checked.

    Returns:
        Whether the number is a prime.
    """
    for i in range(2, round(sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True


def prime_factors(num: int, use_power: bool) -> List:
    """Return the prime factors of the input number.

    Args:
        num: The number whose prime factors are to be returned.
        use_power: If ``True``, return the factors in the format of [[X, Y], [a, b]]
            where num=X**a*Y**b. For example, ``prime_factors(12, False)`` returns
            ``[2, 2, 3]`` and ``prime_factors(12, True)`` returns ``[[2, 3], [2, 1]]``.

    Returns:
        Prime factors.
    """
    factors = []
    i = 2
    while i <= round(sqrt(num))+1:
        if num % i == 0:
            factors = np.append(factors, i)
            num = num / i
        else:
            i = i + 1
    if num != 1:
        factors = np.append(factors, num)
    factors_size = factors.size
    factors2 = [factors[0]]
    powers = [1]
    power_idx = 0
    for i in range(1, factors_size):
        if factors[i] == factors[i-1]:
            powers[power_idx] = powers[power_idx]+1
        if factors[i] != factors[i-1]:
            powers.append(1)
            power_idx = power_idx+1
            factors2.append(factors[i])
    if not use_power:
        return factors
    return [factors2, powers]


def dodis_output_size(
        num_bits: int,
        rate_bt: float,
        rate_sv: float,
        epsilon_dodis: float,
        q_proof: bool
) -> int:
    """Calculate the output size of the Dodis extractor.

    Args:
        num_bits: The 2/3 outcomes bits from each circuit.
        rate_bt: How much randomness is in each bit.
        rate_sv: The assumption on the initial randomness rate f the WSR as
            a Santha-Vazirani source.
        epsilon_dodis: Security parameter defining the distance to uniformity of
            the final bit string.
        q_proof: Whether quantum proof extraction is needed.

    Returns:
        Output size of the Dodis extractor.
    """
    if not q_proof:
        return floor(num_bits * (rate_bt + rate_sv - 1) + 1 - 2 * log2(1 / epsilon_dodis))
    return floor(1 / 5 * (num_bits * (rate_bt + rate_sv - 1) + 1 - 8 *
                          log2(1 / epsilon_dodis) - 8 * log2(sqrt(3) / 2)))


def bt_adjusting(bt_value: float, epsilon: float, delta_finite_stat: int = 0) -> float:
    """Creates an adjustment value related to the probability of error due to finite stats.

    Args:
        bt_value: Bell value.
        epsilon: How close the output string is to that of a perfect distribution.
        delta_finite_stat: Set to zero to assume no finite statistical effects.

    Returns:
        Adjusted Bell value.
    """
    bt_adjusted = (bt_value + delta_finite_stat) / (8 * ((0.5 - epsilon)**3))
    return bt_adjusted


def guessing_probability(bt_adjusted: float) -> float:
    """Calculate the probability an adversary could guess the bell value.

    Also known as the 'predictive power', this probability gives
    an indication of the quality of the randomness.

    Args:
        bt_adjusted: Adjusted bell value.

    Returns:
        The guessing probability.
    """
    if bt_adjusted >= 1 / 16:
        probability = 0.5 + 4 * bt_adjusted
    if bt_adjusted < 1 / 16:
        probability = 0.25 + 2 * bt_adjusted + \
             sqrt(3) * sqrt((bt_adjusted - 4 * (bt_adjusted**2)))
    if bt_adjusted >= 1 / 8:
        probability = 1
    return probability


def hayashi_parameters(
        input_size: int,
        rate_sv: float,
        c_max: int,
        c_penalty: int
) -> Tuple[int, float]:
    """Generate parameters for the Hayashi extractor.

    Args:
        input_size: Size in bits of the input string.
        rate_sv: The assumption on the initial randomness rate of the WSR
            used as a Santha-Vazirani source.
        c_max: Computed maximum value.
        c_penalty: Computed penalty value.

    Returns:
        A tuple consists of the multiplier and the Hayashi epsilon value.

    Raises:
        ValueError: If the parameters are invalid for the second extractor.
    """
    c = c_max - c_penalty
    if c < 2:
        raise ValueError("Invalid parameters for the second extractor.")
    epsilon_hayashi = sqrt(c - 1) * pow(2, input_size / 2 * (c * (1 - rate_sv) - 1))

    return c, epsilon_hayashi


def bitarray_to_bytes(bitarray: List[int]) -> bytes:
    """Convert an array of bits to bytes.

    Args:
        bitarray: Bit array to be converted.

    Returns:
        Input array in bytes.
    """
    n_bits = len(bitarray)
    n_bytes = (n_bits + 7) >> 3
    int_array = [0] * n_bytes
    for i in range(n_bits):
        int_array[i >> 3] |= bitarray[i] << (i & 7)
    return bytes(int_array)


def bytes_to_bitarray(the_bytes: bytes, num_bits: int) -> List[int]:
    """Convert input bytes into an array of bits.

    Args:
        the_bytes: Bytes to be converted.
        num_bits: Number of bits to return.

    Returns:
        An array of bits.
    """
    return [(the_bytes[i >> 3] >> (i & 7)) & 1 for i in range(num_bits)]


def generate_wsr(num_bits: int) -> List[int]:
    """Generate a list of WSR bits.

    Args:
        num_bits: Number of bits needed.

    Returns:
        A list of random binary numbers.
    """
    return list(np.random.randint(2, size=num_bits))
