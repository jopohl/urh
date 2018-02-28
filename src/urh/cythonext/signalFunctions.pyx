# noinspection PyUnresolvedReferences
cimport numpy as np
import cython
import numpy as np
from libcpp cimport bool

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

from urh.cythonext import util

from cython.parallel import prange
# noinspection PyUnresolvedReferences
from libc.math cimport atan2, sqrt, M_PI, sin, cos

cdef:
    float complex imag_unit = 1j

cdef float NOISE_FSK_PSK = -4.0
cdef float NOISE_ASK = 0.0


cdef float calc_costa_alpha(float bw, float damp=1 / sqrt(2)) nogil:
    # BW in range((2pi/200), (2pi/100))
    cdef float alpha = (4 * damp * bw) / (1 + 2 * damp * bw + bw * bw)

    return alpha

cdef float calc_costa_beta(float bw, float damp=1 / sqrt(2)) nogil:
    # BW in range((2pi/200), (2pi/100))
    cdef float beta = (4 * bw * bw) / (1 + 2 * damp * bw + bw * bw)
    return beta


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

cpdef np.ndarray[np.complex64_t, ndim=1] modulate_fsk(unsigned char[:] bit_array,
                                                      unsigned long pause, unsigned long start,
                                                      float a, float freq0, float freq1,
                                                      float phi, float sample_rate,
                                                      unsigned long samples_per_bit):
    cdef long long i, j, index
    cdef float t, f, arg, f_next, phase
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    cdef np.ndarray[np.complex64_t, ndim=1] result = np.zeros(total_samples, dtype=np.complex64)
    cdef float* phases = <float *>malloc(total_samples * sizeof(float))

    for i in range(0, samples_per_bit):
        phases[i] = phi

    with cython.cdivision:
        for i in range(1, len(bit_array)):
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
        result[i] = a*(cos(arg) + imag_unit * sin(arg))

        # We need to correct the phase on transitions between 0 and 1
        # if i < loop_end - 1 and (i+1) % samples_per_bit == 0:
        #     index = <long long>((i+1)/samples_per_bit)
        #     f_next = freq0 if bit_array[index] == 0 else freq1
        #     phi += 2 * M_PI * t * (f - f_next)
        #     phi = phi % (2 * M_PI)

    free(phases)
    return result

cpdef np.ndarray[np.complex64_t, ndim=1] modulate_ask(unsigned char[:] bit_array,
                                                      unsigned long pause, unsigned long start,
                                                      double a0, double a1, double f,
                                                      double phi, double sample_rate,
                                                      unsigned long samples_per_bit):
    cdef long long i, index
    cdef double t, a, arg
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    cdef np.ndarray[np.complex64_t, ndim=1] result = np.zeros(total_samples, dtype=np.complex64)

    cdef long long loop_end = total_samples-pause
    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        a = a0 if bit_array[index] == 0 else a1

        if a > 0:
            t = (i+start) / sample_rate
            arg = 2 * M_PI * f * t + phi
            result[i] = a*(cos(arg) + imag_unit * sin(arg))

    return result

cpdef np.ndarray[np.complex64_t, ndim=1] modulate_psk(unsigned char[:] bit_array,
                                                      unsigned long pause, unsigned long start,
                                                      double a, double f,
                                                      double phi0, double phi1, double sample_rate,
                                                      unsigned long samples_per_bit):
    cdef long long i, index
    cdef double t, phi, arg
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    cdef np.ndarray[np.complex64_t, ndim=1] result = np.zeros(total_samples, dtype=np.complex64)

    cdef long long loop_end = total_samples-pause
    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        phi = phi0 if bit_array[index] == 0 else phi1

        t = (i+start) / sample_rate
        arg = 2 * M_PI * f * t + phi
        result[i] = a*(cos(arg) + imag_unit * sin(arg))

    return result


cdef np.ndarray[np.float64_t, ndim=1] gauss_fir(double sample_rate, unsigned long samples_per_bit,
                                                double bt=.5, double filter_width=1.0):
    """

    :param filter_width: Filter width
    :param bt: normalized 3-dB bandwidth-symbol time product
    :return:
    """
    # http://onlinelibrary.wiley.com/doi/10.1002/9780470041956.app2/pdf
    k = np.arange(-int(filter_width * samples_per_bit), int(filter_width * samples_per_bit) + 1)
    ts = samples_per_bit / sample_rate  # symbol time
    h = np.sqrt((2 * np.pi) / (np.log(2))) * bt / ts * np.exp(
        -(((np.sqrt(2) * np.pi) / np.sqrt(np.log(2)) * bt * k / samples_per_bit) ** 2))
    return h / h.sum()

cpdef np.ndarray[np.complex64_t, ndim=1] modulate_gfsk(unsigned char[:] bit_array,
                                                      unsigned long pause, unsigned long start,
                                                      double a, double freq0, double freq1,
                                                      double phi, double sample_rate,
                                                      unsigned long samples_per_bit,
                                                      double gauss_bt, double filter_width):
    cdef long long i, index
    cdef long long total_samples = int(len(bit_array) * samples_per_bit + pause)

    cdef np.ndarray[np.float64_t, ndim=1] frequencies = np.empty(total_samples - pause, dtype=np.float64)
    cdef long long loop_end = total_samples-pause

    for i in prange(0, loop_end, nogil=True, schedule="static"):
        index = <long long>(i/samples_per_bit)
        frequencies[i] = freq0 if bit_array[index] == 0 else freq1

    cdef np.ndarray[np.float64_t, ndim=1] t = np.arange(start, start + total_samples - pause) / sample_rate
    cdef np.ndarray[np.float64_t, ndim=1] gfir = gauss_fir(sample_rate, samples_per_bit,
                                                           bt=gauss_bt, filter_width=filter_width)

    if len(frequencies) >= len(gfir):
        frequencies = np.convolve(frequencies, gfir, mode="same")
    else:
        # Prevent dimension crash later, because gaussian finite impulse response is longer then param_vector
        frequencies = np.convolve(gfir, frequencies, mode="same")[:len(frequencies)]

    cdef np.ndarray[np.complex64_t, ndim=1] result = np.zeros(total_samples, dtype=np.complex64)

    cdef np.ndarray[np.float64_t, ndim=1] phases = np.empty(len(frequencies), dtype=np.float64)
    phases[0] = phi
    for i in range(0, len(phases) - 1):
         # Correct the phase to prevent spiky jumps
        phases[i + 1] = 2 * M_PI * t[i] * (frequencies[i] - frequencies[i + 1]) + phases[i]

    cdef np.ndarray[np.float64_t, ndim=1] arg = (2 * M_PI * frequencies * t + phases)
    result[:total_samples - pause].real = a * np.cos(arg)
    result[:total_samples - pause].imag = a * np.sin(arg)


    return result

cdef void costa_demod(float complex[::1] samples, float[::1] result, float noise_sqrd,
                          float costa_alpha, float costa_beta, bool qam, long long num_samples):
    cdef float phase_error
    cdef long long i
    cdef float costa_freq = 0
    cdef float costa_phase = 0
    cdef float complex nco_out
    cdef float complex nco_times_sample, c
    cdef float real, imag
    cdef float magnitude

    for i in range(0, num_samples):
        c = samples[i]
        real, imag = c.real, c.imag
        magnitude = real * real + imag * imag
        if magnitude <= noise_sqrd:  # |c| <= mag_treshold
            result[i] = NOISE_FSK_PSK
            continue

        # # NCO Output
        #nco_out = np.exp(-costa_phase * 1j)
        nco_out = cos(-costa_phase) + imag_unit * sin(-costa_phase)

        nco_times_sample = nco_out * c
        phase_error = nco_times_sample.imag * nco_times_sample.real
        costa_freq += costa_beta * phase_error
        costa_phase += costa_freq + costa_alpha * phase_error
        if qam:
            result[i] = magnitude * nco_times_sample.real
        else:
            result[i] = nco_times_sample.real

cpdef np.ndarray[np.float32_t, ndim=1] afp_demod(float complex[::1] samples, float noise_mag, int mod_type):
    if len(samples) <= 2:
        return np.zeros(len(samples), dtype=np.float32)

    cdef long long i, ns
    cdef float complex tmp = 0
    cdef float complex c = 0
    cdef float arg, noise_sqrd, complex_phase, prev_phase, NOISE
    cdef float real = 0
    cdef float imag = 0
    ns = len(samples)

    cdef float[::1] result = np.zeros(ns, dtype=np.float32, order="C")
    cdef float costa_freq = 0
    cdef float costa_phase = 0
    cdef complex nco_out = 0
    cdef float phase_error
    cdef float costa_alpha, costa_beta
    cdef complex nco_times_sample
    cdef float magnitude = 0

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
        for i in prange(1, ns, nogil=True, schedule='static'):
            c = samples[i]
            real, imag = c.real, c.imag
            magnitude = real * real + imag * imag
            if magnitude <= noise_sqrd:  # |c| <= mag_treshold
                result[i] = NOISE
                continue

            if mod_type == 0:  # ASK
                result[i] = magnitude
            elif mod_type == 1:  # FSK
                tmp = samples[i - 1].conjugate() * c
                result[i] = atan2(tmp.imag, tmp.real)  # Freq

    return np.asarray(result)

cpdef unsigned long long find_signal_start(float[::1] demod_samples, int mod_type):

    cdef unsigned long long i, ns, l
    cdef float dsample
    cdef int has_oversteuern, conseq_noise, conseq_not_noise, behind_oversteuern
    cdef float NOISE = get_noise_for_mod_type(mod_type)

    has_oversteuern = 0
    behind_oversteuern = 0
    conseq_noise = 0
    conseq_not_noise = 0

    ns = len(demod_samples)
    l = 100
    if ns < 100:
        l = ns

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

    cdef unsigned long long i
    cdef float dsample
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
    cdef float s, s_prev
    cdef int cur_state, new_state
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
    cdef int i
    cdef float center
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

cdef:
    struct Cluster:
        double sum
        unsigned long long int nitems

cpdef float estimate_qad_center(float[::1] samples, unsigned int num_centers):
    """
    Estimate the centers using Lloyds algorithm
    Use more centers for ks clipping

    :param samples:
    :param num_centers:
    :return:
    """
    cdef unsigned long long nsamples = len(samples)
    if nsamples == 0:
        return 0

    cdef Cluster *clusters = <Cluster *>malloc(num_centers * sizeof(Cluster))

    cdef unsigned long long i

    for i in range(0, num_centers):
        clusters[i].nitems = 0
        clusters[i].sum = 0

    cdef:
        tuple tmp = util.minmax(samples)
        float first_center = tmp[0]
        float last_center = tmp[1]

        float[::1] centers = np.array([ first_center+i*(last_center-first_center)/(num_centers-1)
                                       for i in range(0, num_centers) ], dtype=np.float32)
        float sample
        int center_index = 0



    for i in range(0, nsamples):
        sample = samples[i]
        center_index = find_nearest_center(sample, centers, num_centers)
        clusters[center_index].sum += sample
        clusters[center_index].nitems += 1

    cdef unsigned long long[::1] cluster_lens = np.array([clusters[i].nitems for i in range(num_centers)], dtype=np.uint64)
    # can't to static typing here, because resulting type of argsort depends on x64/x86
    sorted_indexes = np.argsort(cluster_lens)
    cdef float center1, center2
    cdef int index1 = sorted_indexes[len(sorted_indexes)-1]
    cdef int index2 = sorted_indexes[len(sorted_indexes)-2]

    if clusters[index1].nitems > 0:
        center1 = clusters[index1].sum / clusters[index1].nitems # Cluster with most entries
    else:
        center1 = 0

    if clusters[index2].nitems > 0:
        center2 = clusters[index2].sum / clusters[index2].nitems # Cluster with second most entries
    else:
        center2 = 0

    free(clusters)
    return (center1 + center2)/2

cpdef np.ndarray[np.complex64_t, ndim=1] fir_filter(float complex[::1] input_samples, float complex[::1] filter_taps):
    cdef int i, j
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

    cdef long n, j, k
    cdef long M = len(a)
    cdef long N = len(b)
    for n in range(max(M, N+1) , len(signal)):
        for j in range(M):
            result[n] += a[j] * signal[n-j]

        for k in range(N):
            result[n] += b[k] * result[n-1-k]

    return result
