# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np
from libcpp cimport bool

np.import_array()

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
        return np.empty(len(samples), dtype=np.float32)

    cdef long long i, ns
    cdef float complex tmp = 0
    cdef float complex c = 0
    cdef float arg, noise_sqrd, complex_phase, prev_phase, NOISE
    cdef float real = 0
    cdef float imag = 0
    ns = len(samples)

    cdef float[::1] result = np.empty(ns, dtype=np.float32, order="C")
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

cpdef unsigned long long[:, ::1] grab_pulse_lens(float[::1] samples,
                                                 float treshold, unsigned int tolerance, int mod_type):
    """
    Holt sich die Pulslängen aus den quadraturdemodulierten Samples
    @param samples: Samples nach der QAD
    @param treshold: Alles über der Treshold ist ein Einserpuls, alles darunter 0er Puls
    @return: Ein 2D Array arr.
    arr[i] gibt Position an.
    arr[i][0] gibt an ob Einspuls (arr[i][0] = 1) Nullpuls (arr[i][0] = 0) Pause (arr[i][0] = 42)
    arr[i][1] gibt die Länge des Pulses bzw. der Pause an.
    """
    cdef unsigned long long i, ns, pulselen = 0
    cdef unsigned long long cur_index = 0, conseq_ones = 0, conseq_zeros = 0, conseq_pause = 0
    cdef float s, s_prev
    cdef int cur_state
    cdef float NOISE = get_noise_for_mod_type(mod_type)
    ns = len(samples)

    cdef unsigned long long[:, ::1] result = np.empty((ns, 2), dtype=np.uint64, order="C")
    if ns == 0:
        return result

    s_prev = samples[0]
    if s_prev == NOISE:
        cur_state = 42
    elif s_prev > treshold:
        cur_state = 1
    else:
        cur_state = 0

    for i in range(ns-1):
        pulselen += 1
        s = samples[i]
        if s == NOISE:
            conseq_pause += 1
            conseq_ones = 0
            conseq_zeros = 0
            if cur_state == 42: continue
        elif s > treshold:
            conseq_ones += 1
            conseq_zeros = 0
            conseq_pause = 0
            if cur_state == 1: continue
        else:
            conseq_zeros += 1
            conseq_ones = 0
            conseq_pause = 0
            if cur_state == 0: continue

        if conseq_ones > tolerance:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulselen - tolerance
            cur_index += 1
            pulselen = tolerance
            cur_state = 1

        elif conseq_zeros > tolerance:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulselen - tolerance
            cur_index += 1
            pulselen = tolerance
            cur_state = 0

        elif conseq_pause > tolerance:
            result[cur_index, 0] = cur_state
            result[cur_index, 1] = pulselen - tolerance
            cur_index += 1
            pulselen = tolerance
            cur_state = 42

    # Letzen anfügen
    cdef unsigned long long len_result = len(result)
    if cur_index < len_result:
        result[cur_index, 0] = cur_state
        result[cur_index, 1] = pulselen
        cur_index += 1

    if cur_index > len_result:
        cur_index = len_result

    return result[:cur_index]

cdef class Symbol:
    cdef public str name
    cdef public int nbits
    cdef public int pulsetype
    cdef public unsigned long long nsamples # Num Samples for this Symbol. Needed in Modulator.
    def __init__(self, str name, int nbits, int pulsetype, unsigned long long nsamples):
        """
        :param nbits: Number of bits this Symbol covers
        :param name: Name of the symbol (one char)
        :param pulsetype: 0 für 0er Puls, 1 für 1er Puls
        :return:
        """
        self.name = name
        self.pulsetype = pulsetype
        self.nbits = nbits
        self.nsamples = nsamples

    def __repr__(self):
        return "{0} ({1}:{2})".format(self.name, self.pulsetype, self.name)

    def __deepcopy__(self, memo):
        result = Symbol(self.name, self.nbits, self.pulsetype, self.nsamples)
        memo[id(self)] = result
        return result



cpdef unsigned long long estimate_bit_len(float[::1] qad_samples, float qad_center, int tolerance, int mod_type):

    start = find_signal_start(qad_samples, mod_type)
    cdef unsigned long long[:, ::1] ppseq = grab_pulse_lens(qad_samples[start:], qad_center, tolerance, mod_type)
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
    cdef np.ndarray[np.int64_t, ndim=1] sorted_indexes = np.argsort(cluster_lens)
    cdef float center1, center2
    cdef int index1 = sorted_indexes[len(sorted_indexes)-1]
    cdef int index2 = sorted_indexes[len(sorted_indexes)-2]

    if clusters[index1].nitems > 0:
        center1 = clusters[index1].sum / clusters[index1].nitems # Cluster mit den meisten Einträgen
    else:
        center1 = 0

    if clusters[index2].nitems > 0:
        center2 = clusters[index2].sum / clusters[index2].nitems # Cluster mit zweitmeisten Einträgen
    else:
        center2 = 0

    free(clusters)
    return (center1 + center2)/2
