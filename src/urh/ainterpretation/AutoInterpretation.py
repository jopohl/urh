import fractions
import itertools
import math
import sys
from collections import Counter

import numpy as np


def k_means(data: np.ndarray, k=2) -> tuple:
    # todo: cythonize for performance
    centers = np.empty(k, dtype=np.float32)
    clusters = []
    unique = set(data)
    if len(unique) < k:
        print("Warning: less different values than k")
        k = len(unique)

    for i in range(k):
        centers[i] = unique.pop()
        clusters.append([])

    old_centers = np.array(centers)
    old_centers[0] += 1

    while (old_centers ** 2 - centers ** 2).sum() != 0:
        for i in range(k):
            clusters[i].clear()

        for i, sample in enumerate(data):
            distances = np.empty(k, dtype=np.float32)
            for j in range(k):
                distances[j] = (centers[j] - sample) ** 2
            index = int(np.argmin(distances))
            clusters[index].append(sample)

        old_centers = np.array(centers)
        for i in range(k):
            centers[i] = np.mean(clusters[i])

    return centers, clusters


def max_without_outliers(data: np.ndarray, z=3):
    return np.max(data[abs(data - np.mean(data)) < z * np.std(data)])


def detect_noise_level(magnitudes, k=2):
    centers, clusters = k_means(magnitudes, k)

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
    result = []

    if len(magnitudes) == 0:
        return []

    N = len(magnitudes)

    # tolerance / robustness against outliers
    outlier_tolerance = 3
    conseq_above = conseq_below = 0

    # total length of the current plateau i.e. length of current message and pause in samples
    above_total = below_total = 0

    # Three states: 1 = above noise, 0 = in noise, but not yet above k threshold (k * above_total), -1 = in noise
    state = 1 if magnitudes[0] > noise_threshold else -1
    start = 0
    for i in range(N):
        # Process current sample, increase local and total counters depending on current state and sample
        is_above_noise = magnitudes[i] > noise_threshold
        if state == 1:
            above_total += 1
            if is_above_noise:
                conseq_below = 0
            else:
                conseq_below += 1
        elif state == 0 or state == -1:
            below_total += 1
            if is_above_noise:
                conseq_above += 1
            else:
                conseq_above = 0

        # Perform state change if necessary
        if state == 1 and conseq_below >= outlier_tolerance:
            # 1 -> 0
            state = 0
        elif state == 0 and conseq_above >= outlier_tolerance:
            # 0 -> 1
            state = 1
            above_total += below_total
            below_total = 0
        elif state == 0 and below_total >= q * above_total:
            # 0 -> -1
            state = -1
            result.append((start, start + above_total))
            above_total = 0
        elif state == -1 and conseq_above >= outlier_tolerance:
            # -1 -> 1
            state = 1
            start = i - conseq_above
            below_total = 0

    # append last message
    if state in (0, 1) and above_total >= 0:
        result.append((start, start + above_total))

    return result


def detect_center(rectangular_signal: np.ndarray, k=2, z=3):
    rect = rectangular_signal[rectangular_signal > -4]  # do not consider noise
    rect = rect[abs(rect - np.mean(rect)) < z * np.std(rect)]  # remove outliers
    centers, clusters = k_means(rect, k=k)
    return (centers[0] + centers[1]) / 2


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


def get_bit_length_from_plateau_lengths(plateau_lengths):
    if len(plateau_lengths) == 0:
        return 0

    if len(plateau_lengths) == 1:
        return plateau_lengths[0]

    merged_lengths = merge_plateau_lengths(plateau_lengths)
    round_plateau_lengths(merged_lengths)
    return get_tolerant_greatest_common_divisor(merged_lengths)


def estimate(signal: np.ndarray) -> dict:
    magnitudes = np.abs(signal)
    # find noise threshold
    noise = detect_noise_level(magnitudes, k=2)

    # segment messages
    message_indices = segment_messages_from_magnitudes(magnitudes, noise_threshold=noise, q=2)

    # get instantaneous frequency, magnitude, phase of messages
    # foreach of them:
    # estimate centers of messages
    # estimate bitlength of messages
    # score these results to find modulation type

    result = dict()
    result["bit_length"] = 42
    result["modulation_type"] = "ASK"
    result["center"] = 0.02
    result["noise"] = 0.001

    return result
