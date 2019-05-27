# noinspection PyUnresolvedReferences
cimport numpy as np
import cython
import numpy as np
from libcpp cimport bool

from urh.cythonext.util cimport IQ, iq

from cython.parallel import prange
from libc.math cimport atan2, sqrt, M_PI

cdef extern from "math.h" nogil:
    float cosf(float x)
    float sinf(float x)

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

cdef float complex imag_unit = 1j
cdef float NOISE_FSK_PSK = -4.0
cdef float NOISE_ASK = 0.0

cpdef float get_noise_for_mod_type(int mod_type):
    if mod_type == 0:
        return NOISE_ASK
    elif mod_type == 1:
        return NOISE_FSK_PSK
    elif mod_type == 2:
        return NOISE_FSK_PSK
    elif mod_type == 3:  # ASK + PSK (QAM)
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

cpdef modulate_fsk(unsigned char[:] bit_array, unsigned long pause, unsigned long start,
                                      float a, float freq0, float freq1, float phi, float sample_rate,
                                      long long samples_per_bit, iq iq_type):
    cdef long long i = 0, j = 0, index = 0
    cdef float t = 0, f = 0, arg = 0, f_next = 0, phase = 0
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    result = np.zeros((total_samples, 2), dtype=get_numpy_dtype(iq_type))
    cdef iq[:, ::1] result_view = result
    cdef float* phases = <float *>malloc(total_samples * sizeof(float))

    for i in range(0, samples_per_bit):
        phases[i] = phi

    cdef long long num_bits = len(bit_array)
    with cython.cdivision:
        for i in range(1, num_bits):
            phase = phases[i*samples_per_bit-1]

            # We need to correct the phase on transitions between 0 and 1
            if bit_array[i-1] != bit_array[i]:
                t = (i*samples_per_bit+start-1) / sample_rate
                f = freq0 if bit_array[i-1] == 0 else freq1
                f_next = freq0 if bit_array[i] == 0 else freq1
                phase = (phase + 2 * M_PI * t * (f - f_next)) % (2 * M_PI)

            for j in range(i*samples_per_bit, (i+1)*samples_per_bit):
                phases[j] = phase


    cdef long long loop_end = total_samples-pause
    for i in prange(0, loop_end, nogil=True, schedule="static"):
        t = (i+start) / sample_rate
        index = <long long>(i/samples_per_bit)
        f = freq0 if bit_array[index] == 0 else freq1

        arg = 2 * M_PI * f * t + phases[i]
        result_view[i, 0] = <iq>(a * cosf(arg))
        result_view[i, 1] = <iq>(a * sinf(arg))

        # We need to correct the phase on transitions between 0 and 1
        # if i < loop_end - 1 and (i+1) % samples_per_bit == 0:
        #     index = <long long>((i+1)/samples_per_bit)
        #     f_next = freq0 if bit_array[index] == 0 else freq1
        #     phi += 2 * M_PI * t * (f - f_next)
        #     phi = phi % (2 * M_PI)

    free(phases)
    return result

cpdef modulate_ask(unsigned char[:] bit_array, unsigned long pause, unsigned long start,
                            double a0, double a1, double f, double phi, double sample_rate,
                            unsigned long samples_per_bit, iq iq_type):
    cdef long long i = 0, index = 0
    cdef float t = 0, a = 0, arg = 0
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    result = np.zeros((total_samples, 2), dtype=get_numpy_dtype(iq_type))
    cdef iq[:, ::1] result_view = result

    cdef long long loop_end = total_samples-pause
    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        a = a0 if bit_array[index] == 0 else a1

        if a > 0:
            t = (i+start) / sample_rate
            arg = 2 * M_PI * f * t + phi
            result_view[i, 0] = <iq>(a * cosf(arg))
            result_view[i, 1] = <iq>(a * sinf(arg))

    return result

cpdef modulate_psk(unsigned char[:] bit_array, unsigned long pause, unsigned long start,
                  double a, double f, double phi0, double phi1, double sample_rate,
                  unsigned long samples_per_bit, iq iq_type):
    cdef long long i = 0, index = 0
    cdef float t = 0, phi = 0, arg = 0
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    result = np.zeros((total_samples, 2), dtype=get_numpy_dtype(iq_type))
    cdef iq[:, ::1] result_view = result

    cdef long long loop_end = total_samples-pause
    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        phi = phi0 if bit_array[index] == 0 else phi1

        t = (i+start) / sample_rate
        arg = 2 * M_PI * f * t + phi
        result_view[i, 0] = <iq>(a * cosf(arg))
        result_view[i, 1] = <iq>(a * sinf(arg))

    return result


cdef np.ndarray[np.float32_t, ndim=1] gauss_fir(float sample_rate, unsigned long samples_per_bit,
                                                float bt=.5, float filter_width=1.0):
    """

    :param filter_width: Filter width
    :param bt: normalized 3-dB bandwidth-symbol time product
    :return:
    """
    # http://onlinelibrary.wiley.com/doi/10.1002/9780470041956.app2/pdf
    cdef np.ndarray[np.float32_t] k = np.arange(-int(filter_width * samples_per_bit),
                                                int(filter_width * samples_per_bit) + 1,
                                                dtype=np.float32)
    cdef float ts = samples_per_bit / sample_rate  # symbol time
    cdef np.ndarray[np.float32_t] h = np.sqrt((2 * np.pi) / (np.log(2))) * bt / ts * np.exp(
        -(((np.sqrt(2) * np.pi) / np.sqrt(np.log(2)) * bt * k / samples_per_bit) ** 2))
    return h / h.sum()

cpdef modulate_gfsk(unsigned char[:] bit_array, unsigned long pause, unsigned long start,
                    double a, double freq0, double freq1, double phi, double sample_rate,
                    unsigned long samples_per_bit, double gauss_bt, double filter_width, iq iq_type):
    cdef long long i = 0, index = 0
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    cdef np.ndarray[np.float32_t, ndim=1] frequencies = np.empty(total_samples - pause, dtype=np.float32)
    cdef long long loop_end = total_samples-pause

    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        frequencies[i] = freq0 if bit_array[index] == 0 else freq1

    cdef np.ndarray[np.float32_t, ndim=1] t = np.arange(start, start + total_samples - pause, dtype=np.float32) / sample_rate
    cdef np.ndarray[np.float32_t, ndim=1] gfir = gauss_fir(sample_rate, samples_per_bit,
                                                           bt=gauss_bt, filter_width=filter_width)

    if len(frequencies) >= len(gfir):
        frequencies = np.convolve(frequencies, gfir, mode="same")
    else:
        # Prevent dimension crash later, because gaussian finite impulse response is longer then param_vector
        frequencies = np.convolve(gfir, frequencies, mode="same")[:len(frequencies)]

    result = np.zeros((total_samples, 2), dtype=get_numpy_dtype(iq_type))
    cdef iq[:, ::1] result_view = result

    cdef np.ndarray[np.float32_t, ndim=1] phases = np.empty(len(frequencies), dtype=np.float32)
    phases[0] = phi
    for i in range(0, len(phases) - 1):
         # Correct the phase to prevent spiky jumps
        phases[i + 1] = 2 * M_PI * t[i] * (frequencies[i] - frequencies[i + 1]) + phases[i]

    cdef np.ndarray[np.float32_t, ndim=1] arg = (2 * M_PI * frequencies * t + phases)

    cdef long long stop = max(0, total_samples-pause)
    for i in prange(0, stop, nogil=True, schedule="static"):
        result_view[i, 0] = <iq>(a * cosf(arg[i]))
        result_view[i, 1] = <iq>(a * sinf(arg[i]))

    return result

cdef float calc_costa_alpha(float bw, float damp=1 / sqrt(2)) nogil:
    # BW in range((2pi/200), (2pi/100))
    cdef float alpha = (4 * damp * bw) / (1 + 2 * damp * bw + bw * bw)

    return alpha

cdef float calc_costa_beta(float bw, float damp=1 / sqrt(2)) nogil:
    # BW in range((2pi/200), (2pi/100))
    cdef float beta = (4 * bw * bw) / (1 + 2 * damp * bw + bw * bw)
    return beta

cdef void costa_demod(IQ samples, float[::1] result, float noise_sqrd,
                          float costa_alpha, float costa_beta, bool qam, long long num_samples):
    cdef float phase_error = 0
    cdef long long i = 0
    cdef float costa_freq = 0, costa_phase = 0
    cdef float complex nco_out = 0, nco_times_sample = 0
    cdef float real = 0, imag = 0, magnitude = 0

    cdef float scale, shift

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


    cdef real_float, imag_float
    for i in range(0, num_samples):
        real = samples[i, 0]
        imag = samples[i, 1]
        magnitude = real * real + imag * imag
        if magnitude <= noise_sqrd:  # |c| <= mag_treshold
            result[i] = NOISE_FSK_PSK
            continue

        # # NCO Output
        #nco_out = np.exp(-costa_phase * 1j)
        nco_out = cosf(-costa_phase) + imag_unit * sinf(-costa_phase)

        real_float = (real + shift) / scale
        imag_float = (imag + shift) / scale
        nco_times_sample = nco_out * (real_float + imag_unit * imag_float)
        phase_error = nco_times_sample.imag * nco_times_sample.real
        costa_freq += costa_beta * phase_error
        costa_phase += costa_freq + costa_alpha * phase_error
        if qam:
            result[i] = magnitude * nco_times_sample.real
        else:
            result[i] = nco_times_sample.real

cpdef np.ndarray[np.float32_t, ndim=1] afp_demod(IQ samples, float noise_mag, int mod_type):
    if len(samples) <= 2:
        return np.zeros(len(samples), dtype=np.float32)

    cdef long long i = 0, ns = len(samples)
    cdef float arg = 0
    cdef float noise_sqrd = 0
    cdef float complex_phase = 0
    cdef float prev_phase = 0
    cdef float NOISE = 0
    cdef float real = 0
    cdef float imag = 0

    cdef float[::1] result = np.zeros(ns, dtype=np.float32, order="C")
    cdef float costa_freq = 0
    cdef float costa_phase = 0
    cdef complex nco_out = 0
    cdef float complex tmp
    cdef float phase_error = 0
    cdef float costa_alpha = 0
    cdef float costa_beta = 0
    cdef complex nco_times_sample = 0
    cdef float magnitude = 0

    cdef float max_magnitude   # ensure all magnitudes of ASK demod between 0 and 1
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

    # Atan2 liefert Werte im Bereich von -Pi bis Pi
    # Wir nutzen die Magic Constant NOISE_FSK_PSK um Rauschen abzuschneiden
    noise_sqrd = noise_mag * noise_mag
    NOISE = get_noise_for_mod_type(mod_type)
    result[0] = NOISE

    cdef bool qam = False

    if mod_type == 2 or mod_type == 3: # PSK or QAM
        if mod_type == 3:
            qam = True

        costa_alpha = calc_costa_alpha(<float>(2 * M_PI / 100))
        costa_beta = calc_costa_beta(<float>(2 * M_PI / 100))
        costa_demod(samples, result, noise_sqrd, costa_alpha, costa_beta, qam, ns)

    else:
        for i in prange(1, ns, nogil=True, schedule="static"):
            real = samples[i, 0]
            imag = samples[i, 1]
            magnitude = real * real + imag * imag
            if magnitude <= noise_sqrd:  # |c| <= mag_treshold
                result[i] = NOISE
                continue

            if mod_type == 0:  # ASK
                result[i] = sqrt(magnitude) / max_magnitude
            elif mod_type == 1:  # FSK
                #tmp = samples[i - 1].conjugate() * c
                tmp = (samples[i-1, 0] - imag_unit * samples[i-1, 1]) * (real + imag_unit * imag)
                result[i] = atan2(tmp.imag, tmp.real)  # Freq

    return np.asarray(result)

cpdef unsigned long long find_signal_start(float[::1] demod_samples, int mod_type):

    cdef unsigned long i = 0
    cdef unsigned long ns = len(demod_samples)
    cdef unsigned long l = 100
    if ns < 100:
        l = ns

    cdef float dsample = 0
    cdef int has_oversteuern = 0
    cdef int conseq_noise = 0
    cdef int conseq_not_noise = 0
    cdef int behind_oversteuern = 0
    cdef float NOISE = get_noise_for_mod_type(mod_type)

    for i in range(0, l):
        dsample = demod_samples[i]
        if dsample > NOISE:
            has_oversteuern = 1
            break

    for i in range(0, ns):
        dsample = demod_samples[i]

        if dsample == NOISE:
            conseq_noise += 1
            conseq_not_noise = 0
        else:
            conseq_noise = 0
            conseq_not_noise += 1

        if has_oversteuern == 1:
            if has_oversteuern and conseq_noise > 100:
                behind_oversteuern = 1

            if behind_oversteuern and conseq_not_noise == 3:
                return i - 3

        elif conseq_not_noise == 3:
            return i -3

    return 0

cpdef unsigned long long find_signal_end(float[::1] demod_samples, int mod_type):

    cdef unsigned long long i = 0
    cdef float dsample = 0
    cdef int conseq_not_noise = 0
    cdef float NOISE = get_noise_for_mod_type(mod_type)
    cdef unsigned long long ns = len(demod_samples)

    for i in range(ns, 0, -1):
        dsample = demod_samples[i]

        if dsample > NOISE:
            conseq_not_noise += 1

        if conseq_not_noise == 3:
            return i + 3

    return ns

cpdef unsigned long long[:, ::1] grab_pulse_lens(float[::1] samples, float center,
                                                 unsigned int tolerance, int modulation_type, unsigned int bit_length):
    """
    Holt sich die Pulslängen aus den quadraturdemodulierten Samples
    
    @param samples: Samples nach der QAD
    @param center: Alles über der Treshold ist ein Einserpuls, alles darunter 0er Puls
    @return: Ein 2D Array arr.
    arr[i] gibt Position an.
    arr[i][0] gibt an ob Einspuls (arr[i][0] = 1) Nullpuls (arr[i][0] = 0) Pause (arr[i][0] = 42)
    arr[i][1] gibt die Länge des Pulses bzw. der Pause an.
    """
    cdef int is_ask = modulation_type == 0
    cdef unsigned long long i, pulse_length = 0
    cdef unsigned long long cur_index = 0, consecutive_ones = 0, consecutive_zeros = 0, consecutive_pause = 0
    cdef float s = 0, s_prev = 0
    cdef unsigned short cur_state = 0, new_state = 0
    cdef float NOISE = get_noise_for_mod_type(modulation_type)
    cdef unsigned long long num_samples = len(samples)

    cdef unsigned long long[:, ::1] result = np.zeros((num_samples, 2), dtype=np.uint64, order="C")
    if num_samples == 0:
        return result

    s_prev = samples[0]
    if s_prev == NOISE:
        cur_state = 42
    elif s_prev > center:
        cur_state = 1
    else:
        cur_state = 0

    for i in range(num_samples):
        pulse_length += 1
        s = samples[i]
        if s == NOISE:
            consecutive_pause += 1
            consecutive_ones = 0
            consecutive_zeros = 0
            if cur_state == 42:
                continue

        elif s > center:
            consecutive_ones += 1
            consecutive_zeros = 0
            consecutive_pause = 0
            if cur_state == 1:
                continue

        else:
            consecutive_zeros += 1
            consecutive_ones = 0
            consecutive_pause = 0
            if cur_state == 0:
                continue

        if consecutive_ones > tolerance:
            new_state = 1
        elif consecutive_zeros > tolerance:
            new_state = 0
        elif consecutive_pause > tolerance:
            new_state = 42
        else:
            continue

        if is_ask and cur_state == 42 and (pulse_length - tolerance) < bit_length:
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
    cdef unsigned long long len_result = len(result)
    if cur_index < len_result:
        if cur_index > 0 and result[cur_index - 1, 0] == cur_state:
            result[cur_index - 1, 1] += pulse_length - tolerance
        else:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulse_length - tolerance
            cur_index += 1

    return result[:cur_index]

cpdef unsigned long long estimate_bit_len(float[::1] qad_samples, float qad_center, int tolerance, int mod_type):

    start = find_signal_start(qad_samples, mod_type)
    cdef unsigned long long[:, ::1] ppseq = grab_pulse_lens(qad_samples[start:], qad_center, tolerance, mod_type, 0)
    cdef unsigned long long i = 0
    cdef unsigned long long l = len(ppseq)
    for i in range(0, l):
        if ppseq[i, 0] == 1:
            return ppseq[i, 1] # first pulse after pause

    return 100

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


from libc.stdlib cimport malloc, free

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
