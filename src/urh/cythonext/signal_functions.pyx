# noinspection PyUnresolvedReferences
cimport numpy as np
import cython
import numpy as np
from libcpp cimport bool

from libc.stdint cimport uint8_t, uint16_t, uint32_t, int64_t
from libc.stdio cimport printf
from libc.stdlib cimport malloc, free
from urh.cythonext.util cimport IQ, iq, bit_array_to_number

from cython.parallel import prange
from libc.math cimport atan2, sqrt, M_PI, abs

cdef extern from "math.h" nogil:
    float cosf(float x)
    float acosf(float x)
    float sinf(float x)

cdef extern from "complex.h" namespace "std" nogil:
    float arg(float complex x)
    float complex conj(float complex x)

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

cdef int64_t PAUSE_STATE = -1

cdef float complex imag_unit = 1j
cdef float NOISE_FSK_PSK = -4.0
cdef float NOISE_ASK = 0.0

cdef float get_noise_for_mod_type(str mod_type):
    if mod_type == "ASK":
        return NOISE_ASK
    elif mod_type == "FSK":
        return NOISE_FSK_PSK
    elif mod_type == "PSK" or mod_type == "OQPSK":
        return NOISE_FSK_PSK
    elif mod_type == "QAM":
        return NOISE_ASK * NOISE_FSK_PSK
    else:
        return 0

cdef get_numpy_dtype(iq cython_type):
    if str(cython.typeof(cython_type)) == "char":
        return np.int8
    elif str(cython.typeof(cython_type)) == "short":
        return np.int16
    elif str(cython.typeof(cython_type)) == "float":
        return np.float32
    else:
        raise ValueError("dtype {} not supported for modulation".format(cython.typeof(cython_type)))

cpdef modulate_c(uint8_t[:] bits, uint32_t samples_per_symbol, str modulation_type,
                 float[:] parameters, uint16_t bits_per_symbol,
                 float carrier_amplitude, float carrier_frequency, float carrier_phase, float sample_rate,
                 uint32_t pause, uint32_t start, dtype=np.float32,
                 float gauss_bt=0.5, float filter_width=1.0):

    if dtype == np.int8:
        return __modulate(
            bits, samples_per_symbol, modulation_type, parameters, bits_per_symbol, carrier_amplitude,
            carrier_frequency, carrier_phase, sample_rate, pause, start, <char>0, gauss_bt, filter_width
        )
    elif dtype == np.int16:
        return __modulate(
            bits, samples_per_symbol, modulation_type, parameters, bits_per_symbol, carrier_amplitude,
            carrier_frequency, carrier_phase, sample_rate, pause, start, <short>0, gauss_bt, filter_width
        )
    elif dtype == np.float32:
        return __modulate(
            bits, samples_per_symbol, modulation_type, parameters, bits_per_symbol, carrier_amplitude,
            carrier_frequency, carrier_phase, sample_rate, pause, start, <float>0.0, gauss_bt, filter_width
        )
    else:
        raise ValueError("Unsupported dtype for modulation {}".format(dtype))


cpdef __modulate(uint8_t[:] bits, uint32_t samples_per_symbol, str modulation_type,
                 float[:] parameters, uint16_t bits_per_symbol,
                 float carrier_amplitude, float carrier_frequency, float carrier_phase, float sample_rate,
                 uint32_t pause, uint32_t start, iq iq_type,
                 float gauss_bt=0.5, float filter_width=1.0):
    cdef int64_t i = 0, j = 0, index = 0, prev_index=0, s_i = 0, num_bits = len(bits)
    cdef uint32_t total_symbols = int(num_bits // bits_per_symbol)
    cdef int64_t total_samples = total_symbols * samples_per_symbol + pause

    cdef float a = carrier_amplitude, f = carrier_frequency, phi = carrier_phase

    cdef float f_previous = 0, phase_correction = 0
    cdef float t = 0, current_arg = 0

    result = np.zeros((total_samples, 2), dtype=get_numpy_dtype(iq_type))
    if num_bits == 0:
        return result

    cdef iq[:, ::1] result_view = result

    cdef bool is_fsk = modulation_type.lower() == "fsk"
    cdef bool is_ask = modulation_type.lower() == "ask"
    cdef bool is_psk = modulation_type.lower() == "psk"
    cdef bool is_oqpsk = modulation_type.lower() == "oqpsk"
    cdef bool is_gfsk = modulation_type.lower() == "gfsk"

    assert is_fsk or is_ask or is_psk or is_gfsk or is_oqpsk

    cdef uint8_t[:] oqpsk_bits
    if is_oqpsk:
        assert bits_per_symbol == 2
        bits = get_oqpsk_bits(bits)

    cdef np.ndarray[np.float32_t, ndim=2] gauss_filtered_freqs_phases
    if is_gfsk:
        gauss_filtered_freqs_phases = get_gauss_filtered_freqs_phases(bits, parameters, total_symbols,
                                                                      samples_per_symbol, sample_rate, carrier_phase,
                                                                      start, gauss_bt, filter_width)


    cdef float* phase_corrections = NULL
    if is_fsk and total_symbols > 0:
        phase_corrections = <float*>malloc(total_symbols * sizeof(float))
        phase_corrections[0] = 0.0
        for s_i in range(1, total_symbols):
            # Add phase correction to FSK modulation in order to prevent spiky jumps
            index = bit_array_to_number(bits, end=(s_i+1)*bits_per_symbol, start=s_i*bits_per_symbol)
            prev_index = bit_array_to_number(bits, end=s_i*bits_per_symbol, start=(s_i-1)*bits_per_symbol)

            f = parameters[index]
            f_previous = parameters[prev_index]

            if f != f_previous:
                t = (s_i*samples_per_symbol+start-1) / sample_rate
                phase_corrections[s_i] = (phase_corrections[s_i-1] + 2 * M_PI * (f_previous-f) * t) % (2 * M_PI)
            else:
                phase_corrections[s_i] = phase_corrections[s_i-1]

    for s_i in prange(0, total_symbols, schedule="static", nogil=True):
        index = bit_array_to_number(bits, end=(s_i+1)*bits_per_symbol, start=s_i*bits_per_symbol)

        a = carrier_amplitude
        f = carrier_frequency
        phi = carrier_phase
        phase_correction = 0

        if is_ask:
            a = parameters[index]
            if a == 0:
                continue
        elif is_fsk:
            f = parameters[index]
            phase_correction = phase_corrections[s_i]

        elif is_psk or is_oqpsk:
            phi = parameters[index]

        for i in range(s_i * samples_per_symbol, (s_i+1)*samples_per_symbol):
            t = (i+start) / sample_rate
            if is_gfsk:
                f = gauss_filtered_freqs_phases[i, 0]
                phi = gauss_filtered_freqs_phases[i, 1]
            current_arg = 2 * M_PI * f * t + phi + phase_correction

            result_view[i, 0] = <iq>(a * cosf(current_arg))
            result_view[i, 1] = <iq>(a * sinf(current_arg))

    if is_oqpsk:
        for i in range(0, samples_per_symbol):
            result_view[i, 1] = 0
        for i in range(total_samples-pause-samples_per_symbol, total_samples-pause):
            result_view[i, 0] = 0

    if phase_corrections != NULL:
        free(phase_corrections)

    return result

cpdef uint8_t[:] get_oqpsk_bits(uint8_t[:] original_bits):
    # TODO: This method does not work correctly. Fix it when we have a test signal
    cdef int64_t i, num_bits = len(original_bits)
    if num_bits == 0:
        return np.zeros(0, dtype=np.uint8)

    result = np.zeros(num_bits+2, dtype=np.uint8)
    result[0] = original_bits[0]
    result[num_bits+2-1] = original_bits[num_bits-1]

    for i in range(2, num_bits-2, 2):
        result[i] = original_bits[i]
        result[i+1] = original_bits[i-1]

    return result


cdef np.ndarray[np.float32_t, ndim=2] get_gauss_filtered_freqs_phases(uint8_t[:] bits,  float[:] parameters,
                                                                     uint32_t num_symbols, uint32_t samples_per_symbol,
                                                                     float sample_rate, float phi, uint32_t start,
                                                                     float gauss_bt, float filter_width):
    cdef int64_t i, s_i, index, num_values = num_symbols * samples_per_symbol
    cdef np.ndarray[np.float32_t, ndim=1] frequencies = np.empty(num_values, dtype=np.float32)
    cdef uint16_t bits_per_symbol = int(len(bits) // num_symbols)

    for s_i in range(0, num_symbols):
        index = bit_array_to_number(bits, end=(s_i+1)*bits_per_symbol, start=s_i*bits_per_symbol)

        for i in range(s_i * samples_per_symbol, (s_i+1)*samples_per_symbol):
            frequencies[i] = parameters[index]

    cdef np.ndarray[np.float32_t, ndim=1] t = np.arange(start, start + num_values, dtype=np.float32) / sample_rate
    cdef np.ndarray[np.float32_t, ndim=1] gfir = gauss_fir(sample_rate, samples_per_symbol,
                                                           bt=gauss_bt, filter_width=filter_width)

    if len(frequencies) >= len(gfir):
        frequencies = np.convolve(frequencies, gfir, mode="same")
    else:
        # Prevent dimension crash later, because gaussian finite impulse response is longer then param_vector
        frequencies = np.convolve(gfir, frequencies, mode="same")[:len(frequencies)]

    cdef np.ndarray[np.float32_t, ndim=1] phases = np.zeros(len(frequencies), dtype=np.float32)
    phases[0] = phi
    for i in range(0, len(phases) - 1):
         # Correct the phase to prevent spiky jumps
        phases[i + 1] = 2 * M_PI * t[i] * (frequencies[i] - frequencies[i + 1]) + phases[i]

    return np.column_stack((frequencies, phases))

cdef np.ndarray[np.float32_t, ndim=1] gauss_fir(float sample_rate, uint32_t samples_per_symbol,
                                                float bt=.5, float filter_width=1.0):
    """

    :param filter_width: Filter width
    :param bt: normalized 3-dB bandwidth-symbol time product
    :return:
    """
    # http://onlinelibrary.wiley.com/doi/10.1002/9780470041956.app2/pdf
    cdef np.ndarray[np.float32_t] k = np.arange(-int(filter_width * samples_per_symbol),
                                                int(filter_width * samples_per_symbol) + 1,
                                                dtype=np.float32)
    cdef float ts = samples_per_symbol / sample_rate  # symbol time
    cdef np.ndarray[np.float32_t] h = np.sqrt((2 * np.pi) / (np.log(2))) * bt / ts * np.exp(
        -(((np.sqrt(2) * np.pi) / np.sqrt(np.log(2)) * bt * k / samples_per_symbol) ** 2))
    return h / h.sum()

cdef float clamp(float x) nogil:
    if x < -1.0:
        x = -1.0
    elif x > 1.0:
        x = 1.0
    return x

cdef float[::1] costa_demod(IQ samples, float noise_sqrd, int loop_order, float bandwidth=0.1, float damping=sqrt(2.0) / 2.0):
    cdef float alpha = (4 * damping * bandwidth) / (1.0 + 2.0 * damping * bandwidth + bandwidth * bandwidth)
    cdef float beta = (4 * bandwidth * bandwidth) / (1.0 + 2.0 * damping * bandwidth + bandwidth * bandwidth)

    cdef long long i = 0, num_samples = len(samples)
    cdef float real = 0, imag = 0

    cdef float scale, shift, real_float, imag_float, ref_real, ref_imag

    cdef float f1, f2, costa_freq = 0, costa_error = 0, costa_phase = 1.5

    cdef float complex current_sample, nco_out, nco_times_sample

    cdef float[::1] result = np.empty(num_samples, dtype=np.float32)

    if str(cython.typeof(samples)) == "char[:, ::1]":
        scale = 127.5
        shift = 0.5
    elif str(cython.typeof(samples)) == "unsigned char[:, ::1]":
        scale = 127.5
        shift = -127.5
    elif str(cython.typeof(samples)) == "short[:, ::1]":
        scale = 32767.5
        shift = 0.5
    elif str(cython.typeof(samples)) == "unsigned short[:, ::1]":
        scale = 65535.0
        shift = -32767.5
    elif str(cython.typeof(samples)) == "float[:, ::1]":
        scale = 1.0
        shift = 0.0
    else:
        raise ValueError("Unsupported dtype")

    if loop_order > 4:
        # TODO: Adapt this when PSK demodulation with order > 4 shall be supported
        loop_order = 4

    for i in range(1, num_samples):
        real = samples[i, 0]
        imag = samples[i, 1]

        if real * real + imag * imag <= noise_sqrd:
            result[i] = NOISE_FSK_PSK
            continue

        real_float = (real + shift) / scale
        imag_float = (imag + shift) / scale

        current_sample = real_float + imag_unit * imag_float
        nco_out = cosf(-costa_phase) + imag_unit * sinf(-costa_phase)
        nco_times_sample = nco_out * current_sample

        if loop_order == 2:
            costa_error = nco_times_sample.imag * nco_times_sample.real
        elif loop_order == 4:
            f1 = 1.0 if nco_times_sample.real > 0.0 else -1.0
            f2 = 1.0 if nco_times_sample.imag > 0.0 else -1.0
            costa_error = f1 * nco_times_sample.imag - f2 * nco_times_sample.real

        costa_error = clamp(costa_error)

        # advance the loop
        costa_freq += beta * costa_error
        costa_phase += costa_freq + alpha * costa_error

        # wrap the phase
        while costa_phase > (2 * M_PI):
            costa_phase -= 2 * M_PI
        while costa_phase < (-2 * M_PI):
            costa_phase += 2 * M_PI

        costa_freq = clamp(costa_freq)

        if loop_order == 2:
            result[i] = nco_times_sample.real
        elif loop_order == 4:
            result[i] = 2 * nco_times_sample.real + nco_times_sample.imag

    return result


cpdef np.ndarray[np.float32_t, ndim=1] afp_demod(IQ samples, float noise_mag,
                                                 str mod_type, int mod_order, float costas_loop_bandwidth=0.1):
    if len(samples) <= 2:
        return np.zeros(len(samples), dtype=np.float32)

    cdef long long i = 0, ns = len(samples)
    cdef float NOISE = get_noise_for_mod_type(mod_type)
    cdef float noise_sqrd = noise_mag * noise_mag, real = 0, imag = 0, magnitude = 0, max_magnitude
    cdef float complex tmp

    if str(cython.typeof(samples)) == "char[:, ::1]":
        max_magnitude = sqrt(127*127 + 128*128)
    elif str(cython.typeof(samples)) == "unsigned char[:, ::1]":
        max_magnitude = sqrt(255*255)
    elif str(cython.typeof(samples)) == "short[:, ::1]":
        max_magnitude = sqrt(32768*32768 + 32767*32767)
    elif str(cython.typeof(samples)) == "unsigned short[:, ::1]":
        max_magnitude = sqrt(65535*65535)
    elif str(cython.typeof(samples)) == "float[:, ::1]":
        max_magnitude = sqrt(2)
    else:
        raise ValueError("Unsupported dtype")


    if mod_type == "PSK":
        return np.asarray(costa_demod(samples, noise_sqrd, mod_order, bandwidth=costas_loop_bandwidth))

    cdef float[::1] result = np.zeros(ns, dtype=np.float32, order="C")
    result[0] = NOISE

    for i in prange(1, ns, nogil=True, schedule="static"):
        real = samples[i, 0]
        imag = samples[i, 1]
        magnitude = real * real + imag * imag
        if magnitude <= noise_sqrd:  # |c| <= mag_treshold
            result[i] = NOISE
            continue

        if mod_type == "ASK":
            result[i] = sqrt(magnitude) / max_magnitude
        elif mod_type == "FSK":
            #tmp = samples[i - 1].conjugate() * c
            tmp = (samples[i-1, 0] - imag_unit * samples[i-1, 1]) * (real + imag_unit * imag)
            result[i] = atan2(tmp.imag, tmp.real)  # Freq

    return np.asarray(result)

cpdef np.ndarray[np.float32_t, ndim=1] get_center_thresholds(float center, float spacing, int modulation_order):
    cdef np.ndarray[np.float32_t, ndim=1] result = np.empty(modulation_order-1, dtype=np.float32)
    cdef int i, n = modulation_order // 2

    for i in range(0, n):
        result[i] = center - (n-(i+1)) * spacing

    for i in range(n, modulation_order-1):
        result[i] = center + (i+1-n) * spacing

    return result

cpdef int64_t[:, ::1] grab_pulse_lens(float[::1] samples, float center, uint16_t tolerance,
                                      str modulation_type, uint32_t samples_per_symbol,
                                      uint8_t bits_per_symbol=1, float center_spacing=0.1):
    """
    Get the pulse lengths after quadrature demodulation

    arr[i][0] gives type of symbol e.g. (arr[i][0] = 1) and (arr[i][0] = 0) for binary modulation
             Pause is (arr[i][0] = -1)
    arr[i][1] gives length of pulse
    """
    cdef bool is_ask = modulation_type == "ASK"
    cdef int64_t i, j, pulse_length = 0, num_samples = len(samples)
    cdef int64_t cur_index = 0, consecutive_ones = 0, consecutive_zeros = 0, consecutive_pause = 0
    cdef float s = 0, s_prev = 0
    cdef int cur_state = 0, new_state = 0, tmp_state = 0
    cdef float NOISE = get_noise_for_mod_type(modulation_type)

    cdef int modulation_order = 2**bits_per_symbol
    cdef int k


    cdef np.ndarray[np.float32_t, ndim=1] thresholds = get_center_thresholds(center, center_spacing, modulation_order)

    cdef int64_t[:, ::1] result = np.zeros((num_samples, 2), dtype=np.int64, order="C")
    if num_samples == 0:
        return result

    cdef int64_t[:] state_count = np.zeros(modulation_order, dtype=np.int64)

    s_prev = samples[0]
    if s_prev == NOISE:
        cur_state = PAUSE_STATE
    else:
        cur_state = modulation_order - 1
        for k in range(modulation_order - 1):
            if s <= thresholds[k]:
                cur_state = k
                break

    for i in range(num_samples):
        pulse_length += 1
        s = samples[i]

        if s == NOISE:
            tmp_state = PAUSE_STATE
        else:
            tmp_state = modulation_order - 1
            for k in range(modulation_order - 1):
                if s <= thresholds[k]:
                    tmp_state = k
                    break

        if tmp_state == PAUSE_STATE:
            consecutive_pause += 1
        else:
            consecutive_pause = 0

        for j in range(0, modulation_order):
            if j == tmp_state:
                state_count[j] += 1
            else:
                state_count[j] = 0

        if cur_state == tmp_state:
            continue

        new_state = -42

        if consecutive_pause > tolerance:
            new_state = PAUSE_STATE
        else:
            for j in range(0, modulation_order):
                if state_count[j] > tolerance:
                    new_state = j
                    break

        if new_state == -42:
            continue

        if is_ask and cur_state == PAUSE_STATE and (pulse_length - tolerance) < samples_per_symbol:
            # Aggregate short pauses for ASK
            cur_state = 0

        if cur_index > 0 and result[cur_index - 1, 0] == cur_state:
            result[cur_index - 1, 1] += pulse_length - tolerance
        else:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulse_length - tolerance
            cur_index += 1

        pulse_length = tolerance
        cur_state = new_state

    # Append last one
    cdef int64_t len_result = len(result)
    if cur_index < len_result:
        if cur_index > 0 and result[cur_index - 1, 0] == cur_state:
            result[cur_index - 1, 1] += pulse_length - tolerance
        else:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulse_length - tolerance
            cur_index += 1

    return result[:cur_index]

cpdef int find_nearest_center(float sample, float[::1] centers, int num_centers) nogil:
    cdef int i = 0
    cdef float center = 0
    cdef int result = 0
    cdef float min_diff = 99999
    cdef float cur_diff = 0

    for i in range(0, num_centers):
        center = centers[i]
        cur_diff = (sample - center) * (sample - center)
        if cur_diff < min_diff:
            min_diff = cur_diff
            result = i

    return result

cpdef np.ndarray[np.complex64_t, ndim=1] fir_filter(float complex[::1] input_samples, float complex[::1] filter_taps):
    cdef int i = 0, j = 0
    cdef int N = len(input_samples)
    cdef int M = len(filter_taps)
    cdef np.ndarray[np.complex64_t, ndim=1] output = np.zeros(N+M-1, dtype=np.complex64)


    for i in range(N):
        for j in range(M):
            output[i+j] += input_samples[i] * filter_taps[j]


    return output[:N]

cpdef np.ndarray[np.complex64_t, ndim=1] iir_filter(np.ndarray[np.float64_t, ndim=1] a,
                                                    np.ndarray[np.float64_t, ndim=1] b,
                                                    np.ndarray[np.complex64_t, ndim=1] signal):
    cdef np.ndarray[np.complex64_t, ndim=1] result = np.zeros(len(signal), dtype=np.complex64)

    cdef long n = 0, j = 0, k = 0
    cdef long M = len(a)
    cdef long N = len(b)
    for n in range(max(M, N+1) , len(signal)):
        for j in range(M):
            result[n] += a[j] * signal[n-j]

        for k in range(N):
            result[n] += b[k] * result[n-1-k]

    return result
