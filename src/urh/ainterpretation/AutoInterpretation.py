import fractions
import itertools
import math
import sys
from collections import Counter, defaultdict

import numpy as np

from urh.ainterpretation import Wavelet
from urh.cythonext import auto_interpretation as cy_auto_interpretation
from urh.cythonext import signal_functions


def max_without_outliers(data: np.ndarray, z=3):
    if len(data) == 0:
        return None

    return np.max(data[abs(data - np.mean(data)) <= z * np.std(data)])


def min_without_outliers(data: np.ndarray, z=2):
    if len(data) == 0:
        return None

    return np.min(data[abs(data - np.mean(data)) <= z * np.std(data)])


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


def detect_noise_level(magnitudes):
    if len(magnitudes) <= 3:
        return 0

    # 1% for best accuracy and performance for large signals
    chunksize_percent = 1
    chunksize = max(1, int(len(magnitudes) * chunksize_percent / 100))

    chunks = [magnitudes[i - chunksize:i] for i in range(len(magnitudes), 0, -chunksize) if i - chunksize >= 0]

    mean_values = np.fromiter((np.mean(chunk) for chunk in chunks), dtype=np.float32, count=len(chunks))
    if np.std(mean_values) <= 0.001:
        # Mean values are very close to each other, so there is probably no noise in the signal
        return 0

    # Get all indices for values which are in range of 10% of minimum mean value
    indices = np.nonzero(mean_values <= 1.1 * np.min(mean_values))[0]

    return np.max([np.max(chunks[i]) for i in indices])


def segment_messages_from_magnitudes(magnitudes: np.ndarray, noise_threshold: float):
    """
    Get the list of start, end indices of messages

    :param magnitudes: Magnitudes of samples
    :param q: Factor which controls how many samples of previous above noise plateau must be under noise to be counted as noise
    :return:
    """
    return cy_auto_interpretation.segment_messages_from_magnitudes(magnitudes, noise_threshold)


def merge_message_segments_for_ook(segments: list):
    if len(segments) <= 1:
        return segments

    result = []
    # Get a array of pauses for comparision
    pauses = np.fromiter(
        (segments[i + 1][0] - segments[i][1] for i in range(len(segments) - 1)),
        count=len(segments) - 1,
        dtype=np.uint64
    )

    pulses = np.fromiter(
        (segments[i][1] - segments[i][0] for i in range(len(segments))),
        count=len(segments),
        dtype=np.uint64
    )

    # Find relatively large pauses, these mark new messages
    min_pulse_length = min_without_outliers(pulses, z=2)
    large_pause_indices = np.nonzero(pauses >= 8 * min_pulse_length)[0]

    # Merge Pulse Lengths between long pauses
    for i in range(0, len(large_pause_indices) + 1):
        if i == 0:
            start, end = 0, large_pause_indices[i] + 1 if len(large_pause_indices) >= 1 else len(segments)
        elif i == len(large_pause_indices):
            start, end = large_pause_indices[i - 1] + 1, len(segments)
        else:
            start, end = large_pause_indices[i - 1] + 1, large_pause_indices[i] + 1

        msg_begin = segments[start][0]
        msg_length = sum(segments[j][1] - segments[j][0] for j in range(start, end))
        msg_length += sum(segments[j][0] - segments[j - 1][1] for j in range(start + 1, end))

        result.append((msg_begin, msg_begin + msg_length))

    return result

def detect_modulation(data: np.ndarray, wavelet_scale=4, median_filter_order=11) -> str:
    n_data = len(data)
    data = data[np.abs(data) > 0]
    if n_data - len(data) > 3:
        return "OOK"

    data = data / np.abs(np.max(data))
    mag_wavlt = np.abs(Wavelet.cwt_haar(data, scale=wavelet_scale))
    norm_mag_wavlt = np.abs(Wavelet.cwt_haar(data / np.abs(data), scale=wavelet_scale))

    var_mag = np.var(mag_wavlt)
    var_norm_mag = np.var(norm_mag_wavlt)

    var_filtered_mag = np.var(cy_auto_interpretation.median_filter(mag_wavlt, k=median_filter_order))
    var_filtered_norm_mag = np.var(cy_auto_interpretation.median_filter(norm_mag_wavlt, k=median_filter_order))

    if all(v < 0.1 for v in (var_mag, var_norm_mag, var_filtered_mag, var_filtered_norm_mag)):
        return "OOK"

    if var_mag > 1.5 * var_norm_mag:
        # ASK or QAM
        # todo: consider qam, compare filtered mag and filtered norm mag
        return "ASK"
    else:
        # FSK or PSK
        if var_mag > 1.5 * var_filtered_mag:
            return "PSK"
        else:
            # Now we either have a FSK signal or we a have OOK single pulse
            # If we have an FSK, there should be at least two peaks in FFT
            fft = np.fft.fft(data[0:2**int(np.log2(len(data)))])
            fft = np.abs(np.fft.fftshift(fft))
            ten_greatest_indices = np.argsort(fft)[::-1][0:10]
            greatest_index = ten_greatest_indices[0]
            greatest = fft[greatest_index]
            min_distance = 10
            min_freq = int(0.25 * greatest)

            if any(abs(i - greatest_index) >= min_distance and fft[i] >= min_freq for i in ten_greatest_indices):
                return "FSK"
            else:
                return "OOK"

def detect_center(rectangular_signal: np.ndarray):
    rect = rectangular_signal[rectangular_signal > -4]  # do not consider noise
    y, x = np.histogram(rect, bins=16)

    num_values = 2
    most_common_levels = []
    used_indices = set()
    for index in np.argsort(y)[::-1]:
        if not any(i in range(index - 1, index + 2) for i in used_indices):
            used_indices.add(index)
            most_common_levels.append(x[index])
        if len(most_common_levels) == num_values:
            break

    # todo if num values greater two return more centers
    return np.mean(most_common_levels)


def get_plateau_lengths(rect_data, center, percentage=25) -> np.ndarray:
    if len(rect_data) == 0 or center is None:
        return np.array([], dtype=np.uint64)

    state = -1 if rect_data[0] <= center else 1
    plateau_length = 0

    result = []
    current_sum = 0

    for sample in rect_data:
        if current_sum >= int(percentage * len(rect_data) / 100):
            break

        new_state = -1 if sample <= center else 1
        if state == new_state:
            plateau_length += 1
        else:
            result.append(plateau_length)
            current_sum += plateau_length
            state = new_state
            plateau_length = 1

    return np.array(result, dtype=np.uint64)


def estimate_tolerance_from_plateau_lengths(plateau_lengths, relative_max=0.05) -> int:
    if len(plateau_lengths) <= 1:
        return None

    unique, counts = np.unique(plateau_lengths, return_counts=True)
    maximum = max_without_outliers(unique, z=2)

    limit = relative_max * maximum
    # limit = np.mean(plateau_lengths) - 1 * np.std(plateau_lengths)
    if unique[0] > 1 and unique[0] >= limit:
        return 0

    result = 0
    for value in unique:
        if value > 1 and value >= limit:
            break
        result = value

    return result


def merge_plateau_lengths(plateau_lengths, tolerance=None) -> list:
    if tolerance is None:
        tolerance = estimate_tolerance_from_plateau_lengths(plateau_lengths)

    if tolerance == 0 or tolerance is None:
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
    digit_counts = [len(str(p)) for p in plateau_lengths]
    n_digits = min(3, int(np.percentile(digit_counts, 50)))
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


def get_bit_length_from_plateau_lengths(merged_plateau_lengths) -> int:
    if len(merged_plateau_lengths) == 0:
        return 0

    if len(merged_plateau_lengths) == 1:
        return int(merged_plateau_lengths[0])

    round_plateau_lengths(merged_plateau_lengths)

    # filtered = [
    #     min(x, y) for x, y in itertools.combinations(merged_plateau_lengths, 2)
    #     if x != 0 and y != 0 and max(x, y) / min(x, y) - int(max(x, y) / min(x, y)) < 0.2
    # ]

    filtered = cy_auto_interpretation.filter_plateau_lengths(np.array(merged_plateau_lengths, dtype=np.uint64))

    if len(filtered) == 0:
        return 0
    else:
        # Ensure we return a Python Integer to be harmonic with demodulator API
        return int(np.percentile(filtered, 10, interpolation="lower"))


def can_be_psk(rect_data: np.ndarray, z=3):
    rect_data = rect_data[rect_data > -4]  # do not consider noise
    if len(rect_data) == 0:
        return False

    outlier_free_data = rect_data[abs(rect_data - np.mean(rect_data)) <= z * np.std(rect_data)]
    if len(outlier_free_data) == 0:
        return False

    minimum, maximum = np.min(outlier_free_data), np.max(outlier_free_data)
    return np.abs(maximum - minimum) >= np.pi / 2


def can_be_fsk(rect_data: np.ndarray, z=3):
    rect_data = rect_data[rect_data > -4]  # do not consider noise
    if len(rect_data) == 0:
        return False

    outlier_free_data = rect_data[abs(rect_data - np.mean(rect_data)) <= z * np.std(rect_data)]
    if len(outlier_free_data) == 0:
        return False

    minimum, maximum = np.min(outlier_free_data), np.max(outlier_free_data)
    return np.abs(maximum - minimum) >= np.pi / 8


def can_be_ask(rect_data: np.ndarray, z=3):
    rect_data = rect_data[rect_data > -4]  # do not consider noise
    if len(rect_data) == 0:
        return False

    outlier_free_data = rect_data[abs(rect_data - np.mean(rect_data)) <= z * np.std(rect_data)]
    if len(outlier_free_data) <= 1:
        return False

    return np.max(np.diff(outlier_free_data)) >= 0.1


def estimate(signal: np.ndarray) -> dict:
    magnitudes = np.abs(signal)
    # find noise threshold
    noise = detect_noise_level(magnitudes)

    # segment messages
    message_indices = segment_messages_from_magnitudes(magnitudes, noise_threshold=noise)

    # detect modulation
    modulations_for_messages = []
    for start, end in message_indices:
        modulations_for_messages.append(detect_modulation(signal[start:end]))

    modulation = max(set(modulations_for_messages), key=modulations_for_messages.count)
    if modulation == "OOK":
        message_indices = merge_message_segments_for_ook(message_indices)

    if modulation == "OOK" or modulation == "ASK":
        data = signal_functions.afp_demod(signal, noise, 0)
    elif modulation == "FSK":
        data = signal_functions.afp_demod(signal, noise, 1)
    elif modulation == "PSK":
        data = signal_functions.afp_demod(signal, noise, 2)
    else:
        raise ValueError("Unsupported Modulation")

    centers = []
    bit_lengths = []
    tolerances = []
    for start, end in message_indices:
        msg_rect_data = data[start:end]

        center = detect_center(msg_rect_data)

        plateau_lengths = get_plateau_lengths(msg_rect_data, center, percentage=25)
        tolerance = estimate_tolerance_from_plateau_lengths(plateau_lengths)
        if tolerance is None:
            tolerance = 0
        else:
            tolerances.append(tolerance)

        merged_lengths = merge_plateau_lengths(plateau_lengths, tolerance=tolerance)
        if len(merged_lengths) < 2:
            continue

        bit_length = get_bit_length_from_plateau_lengths(merged_lengths)

        min_bit_length = tolerance + 1

        if bit_length > min_bit_length:
            # only add to score if found bit length surpasses minimum bit length
            centers.append(center)
            bit_lengths.append(bit_length)

    # Since we cannot have different centers per message (yet) we need to combine them to return a common center
    if modulation == "OOK" or modulation == "ASK":
        # for ask modulations the center tends to be the minimum of all found centers
        center = min_without_outliers(np.array(centers), z=2)
        if center is None:
            # did not find any centers at all so we cannot return a valid estimation
            return None
    else:
        # for other modulations it is a better strategy to take the mean of found centers
        center = np.mean(centers)

    bit_length = get_most_frequent_value(bit_lengths)

    try:
        tolerance = np.percentile(tolerances, 50, interpolation="lower")
    except IndexError:
        # no tolerances found, default to 5% of bit length
        tolerance = max(1, int(0.05 * bit_length))

    result = {
        "modulation_type": "ASK" if modulation == "OOK" else modulation,
        "bit_length": bit_length,
        "center": center,
        "tolerance": tolerance,
        "noise": noise
    }

    return result
