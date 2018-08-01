import fractions
import itertools
import math
import sys
import time
from collections import Counter, defaultdict

import numpy as np

from urh.cythonext import auto_interpretation as cy_auto_interpretation
from urh.cythonext import signal_functions


def max_without_outliers(data: np.ndarray, z=3):
    return np.max(data[abs(data - np.mean(data)) < z * np.std(data)])


def get_most_frequent_value(values: list):
    """
    Return the most frequent value in list.
    If there is no unique one, return the maximum of the most frequent values

    :param values:
    :return:
    """
    if len(values) == 0:
        return None

    most_common = Counter(values).most_common()
    result, max_count = most_common[0]
    for value, count in most_common:
        if count < max_count:
            return result
        else:
            result = value

    return result


def detect_noise_level(magnitudes, k=2):
    centers, clusters = cy_auto_interpretation.k_means(magnitudes, k)

    if np.max(centers) / np.min(centers) < 1.1:
        # Centers differ less than 10%. Since they are so close, there is probably no noise in the signal.
        return 0

    cluster_sizes = [len(c) for c in clusters]

    if min(cluster_sizes) / max(cluster_sizes) < 0.01:
        # Smaller cluster is less than 1% of the size of the greater. These are presumably outliers and not noise.
        return 0

    noise_cluster = np.array(clusters[np.argmin(centers)])
    return max_without_outliers(noise_cluster, z=3)


def segment_messages_from_magnitudes(magnitudes: np.ndarray, noise_threshold: float, q=2):
    """
    Get the list of start, end indices of messages

    :param magnitudes: Magnitudes of samples
    :param q: Factor which controls how many samples of previous above noise plateau must be under noise to be counted as noise
    :return:
    """
    return cy_auto_interpretation.segment_messages_from_magnitudes(magnitudes, noise_threshold, q=q)


def detect_center(rectangular_signal: np.ndarray, k=2, z=3):
    rect = rectangular_signal[rectangular_signal > -4]  # do not consider noise
    rect = rect[abs(rect - np.mean(rect)) < z * np.std(rect)]  # remove outliers
    centers, clusters = cy_auto_interpretation.k_means(rect, k=k)
    return (centers[0] + centers[1]) / 2


def get_plateau_lengths(rect_data, center, num_flanks=-1):
    if len(rect_data) == 0:
        return []

    state = -1 if rect_data[0] <= center else 1
    plateau_length = 0

    result = []

    for sample in rect_data:
        if num_flanks >= 0 and len(result) >= num_flanks:
            break

        new_state = -1 if sample <= center else 1
        if state == new_state:
            plateau_length += 1
        else:
            result.append(plateau_length)
            state = new_state
            plateau_length = 1

    return result


def estimate_tolerance_from_plateau_lengths(plateau_lengths, relative_max=0.05) -> int:
    if len(plateau_lengths) <= 1:
        return 0

    unique, counts = np.unique(plateau_lengths, return_counts=True)
    maximum = max(plateau_lengths)
    if unique[0] > 1 and unique[0] >= relative_max * maximum:
        return 0

    result = 0
    for value in unique:
        if value > 1 and value >= relative_max * maximum:
            break
        result = value

    return result


def merge_plateau_lengths(plateau_lengths, tolerance=None) -> list:
    if tolerance is None:
        tolerance = estimate_tolerance_from_plateau_lengths(plateau_lengths)

    if tolerance == 0:
        return plateau_lengths

    result = []
    if len(plateau_lengths) == 0:
        return result

    if plateau_lengths[0] <= tolerance:
        result.append(0)

    i = 0
    while i < len(plateau_lengths):
        if plateau_lengths[i] <= tolerance:
            # Look forward to see if we need to merge a larger window e.g. for 67, 1, 10, 1, 21
            n = 2
            while i + n < len(plateau_lengths) and plateau_lengths[i + n] <= tolerance:
                n += 2

            result[-1] = sum(plateau_lengths[max(i - 1, 0):i + n])
            i += n
        else:
            result.append(plateau_lengths[i])
            i += 1

    return result


def round_plateau_lengths(plateau_lengths: list):
    """
    Round plateau lengths to next divisible number of digit count e.g. 99 -> 100, 293 -> 300

    :param plateau_lengths:
    :return:
    """
    # round to n_digits of most common value
    n_digits = len(str(Counter(plateau_lengths).most_common(1)[0][0]))
    f = 10 ** (n_digits - 1)

    for i, plateau_len in enumerate(plateau_lengths):
        plateau_lengths[i] = int(round(plateau_len / f)) * f


def get_tolerant_greatest_common_divisor(numbers):
    """
    Get the greatest common divisor of the numbers in a tolerant manner:
    Calculate each gcd of each pair of numbers and return the most common one

    """
    gcd = math.gcd if sys.version_info >= (3, 5) else fractions.gcd

    gcds = np.array([gcd(x, y) for x, y in itertools.combinations(numbers, 2) if gcd(x, y) != 1])
    if len(gcds) == 0:
        return 1

    values, counts = np.unique(gcds, return_counts=True)
    most_frequent_indices = np.nonzero(counts == np.max(counts))
    return np.max(values[most_frequent_indices])


def get_bit_length_from_plateau_lengths(plateau_lengths, tolerance=None):
    if len(plateau_lengths) == 0:
        return 0

    if len(plateau_lengths) == 1:
        return plateau_lengths[0]

    merged_lengths = merge_plateau_lengths(plateau_lengths, tolerance=tolerance)
    round_plateau_lengths(merged_lengths)
    return get_tolerant_greatest_common_divisor(merged_lengths)


def estimate(signal: np.ndarray) -> dict:
    t = time.time()
    magnitudes = np.abs(signal)
    print("Time magnitudes", time.time()-t)
    # find noise threshold
    t = time.time()
    noise = detect_noise_level(magnitudes, k=2)
    print("time noise", time.time()-t)

    # segment messages
    message_indices = segment_messages_from_magnitudes(magnitudes, noise_threshold=noise, q=2)
    print(message_indices)

    # get instantaneous frequency, magnitude, phase of messages
    insta_magnitudes = signal_functions.afp_demod(signal, noise, 0)
    insta_frequencies = signal_functions.afp_demod(signal, noise, 1)
    insta_phases = signal_functions.afp_demod(signal, noise, 2)

    centers_by_modulation_type = defaultdict(list)
    bit_lengths_by_modulation_type = defaultdict(list)
    tolerances_by_modulation_type = defaultdict(list)

    data = {"ASK": insta_magnitudes, "FSK": insta_frequencies, "PSK": insta_phases}
    plateau_scores = defaultdict(float)

    for mod_type in ("ASK", "FSK", "PSK"):
        for start, end in message_indices:
            msg_rect_data = data[mod_type][start:end]
            center = detect_center(msg_rect_data, k=2, z=3)
            centers_by_modulation_type[mod_type].append(center)

            plateau_lengths = get_plateau_lengths(msg_rect_data, center, num_flanks=32)
            tolerance = estimate_tolerance_from_plateau_lengths(plateau_lengths)
            tolerances_by_modulation_type[mod_type].append(tolerance)

            bit_length = get_bit_length_from_plateau_lengths(plateau_lengths, tolerance=tolerance)
            bit_lengths_by_modulation_type[mod_type].append(bit_length)

            # use abs(p-bit_length) % bit_length so e.g. 290 gets diff of 10 for bit length 300 instad of 290
            plateau_scores[mod_type] += bit_length / (1 + sum((abs(p-bit_length) % bit_length) / bit_length for p in plateau_lengths))
            # TODO: If bit length gets very big, this can go wrong. We could e.g. check if bit_length >= 0.8 * (end-start)
            # However, then we could not work with num flanks

    result_mod_type = max(plateau_scores, key=plateau_scores.get)
    result = {
        "modulation_type": result_mod_type,
        "bit_length": get_most_frequent_value(bit_lengths_by_modulation_type[result_mod_type]),
        "center": get_most_frequent_value(centers_by_modulation_type[result_mod_type]),
        "tolerance": get_most_frequent_value(tolerances_by_modulation_type[result_mod_type]),
        "noise": noise
    }

    return result
