cimport cairspy
from cpython cimport array
import array

ctypedef unsigned char uint8_t
ctypedef unsigned int uint32_t
ctypedef unsigned long long uint64_t

cdef cairspy.airspy_device* _c_device

cpdef open_by_serial(uint64_t serial_number):
    return cairspy.airspy_open_sn(&_c_device, serial_number)

cpdef open():
    return cairspy.airspy_open(&_c_device)

cpdef close():
    return cairspy.airspy_close(_c_device)

cpdef array.array get_sample_rates():
    cdef uint32_t count = 0
    result = cairspy.airspy_get_samplerates(_c_device, &count, 0)
    if result != cairspy.airspy_error.AIRSPY_SUCCESS:
        return array.array('I', [])

    cdef array.array sample_rates = array.array('I', [0]*count)
    result = cairspy.airspy_get_samplerates(_c_device, &sample_rates.data.as_uints[0], count)

    if result == cairspy.airspy_error.AIRSPY_SUCCESS:
        return sample_rates
    else:
        return array.array('I', [])

cpdef int set_sample_rate(uint32_t sample_rate):
    """
    Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list 
    """
    cairspy.airspy_set_samplerate(_c_device, sample_rate)

cpdef int set_center_frequency(uint32_t freq_hz):
    """
    Parameter freq_hz shall be between 24000000(24MHz) and 1750000000(1.75GHz)
    """
    return cairspy.airspy_set_freq(_c_device, freq_hz)

cpdef int set_lna_gain(uint8_t lna_gain):
    """
    Shall be between 0 and 15
    """
    return cairspy.airspy_set_lna_gain(_c_device, lna_gain)

cpdef int set_mixer_gain(uint8_t mixer_gain):
    """
    Shall be between 0 and 15
    """
    return cairspy.airspy_set_mixer_gain(_c_device, mixer_gain)

cpdef int set_vga_gain(uint8_t vga_gain):
    """
    Shall be between 0 and 15
    """
    return cairspy.airspy_set_vga_gain(_c_device, vga_gain)

cpdef int start_rx():
    cairspy.airspy_set_sample_type(_c_device, cairspy.airspy_sample_type.AIRSPY_SAMPLE_FLOAT32_IQ)
    pass # todo

cpdef int stop_rx():
    return cairspy.airspy_stop_rx(_c_device)

cpdef str error_name(cairspy.airspy_error error_code):
    cdef const char* c_error_name = cairspy.airspy_error_name(error_code)
    return c_error_name.decode('UTF-8')
