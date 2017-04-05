from climesdr cimport *
from libc.stdlib cimport malloc

cdef lms_device_t *_c_device

cpdef list get_device_list():
    """
    Obtain a list of LMS devices attached to the system
    """
    cdef lms_info_str_t *dev_list = <lms_info_str_t *> malloc(256 * sizeof(lms_info_str_t))
    result = LMS_GetDeviceList(dev_list)
    if result > 0:
        return [dev_list[i].decode('UTF-8') for i in range(0, result)]
    else:
        return []

cpdef int open(str info=None):
    """
    Opens device specified by the provided ::lms_dev_info string
    This function should be used to open a device based upon the results of LMS_GetDeviceList()
    device should be initialized to NULL 
    :return 0 on success, (-1) on failure
    """
    cdef char*c_info
    if info is None:
        c_info = NULL
    else:
        info_byte_string = info.encode('UTF-8')
        c_info = <char *> info_byte_string

    return LMS_Open(&_c_device, c_info, NULL)

cpdef int close():
    """
    Close device
    :return:  0 on success, (-1) on failure
    """
    return LMS_Close(_c_device)

cpdef int disconnect():
    """
    Disconnect device but keep configuration cache (device is not deallocated).
    :return:  0 on success, (-1) on failure
    """
    return LMS_Disconnect(_c_device)

cpdef bool is_open(int port):
    return LMS_IsOpen(_c_device, port)

cpdef int init():
    """
    Configure LMS chip with settings that make it ready for operation.
 
    This configuration differs from default LMS chip configuration which is
    described in chip datasheet. In order to load default chip configuration use LMS_Reset().
    :return: 0 on success, (-1) on failure
    """
    return LMS_Init(_c_device)

cpdef int get_num_channels(bool dir_tx):
    """
    Obtain number of RX or TX channels. Use this to determine the maximum
    channel index (specifying channel index is required by most API functions).
    The maximum channel index is N-1, where N is number returned by this function
    :param dir_tx: Select RX or TX
    :return:  Number of channels on success, (-1) on failure
    """
    return LMS_GetNumChannels(_c_device, dir_tx)

cpdef int enable_channel(bool dir_tx, size_t chan, bool enabled):
    """
    Enable or disable specified RX channel.
    
    :param dir_tx: Select RX or TX
    :param chan: Channel index
    :param enabled: true(1) to enable, false(0) to disable.
    :return:  0 on success, (-1) on failure
    """
    return LMS_EnableChannel(_c_device, dir_tx, chan, enabled)

cpdef int set_sample_rate(float_type rate, size_t oversample):
    """
    Set sampling rate for all RX/TX channels. Sample rate is in complex samples
    (1 sample = I + Q). The function sets sampling rate that is used for data
    exchange with the host. It also allows to specify higher sampling rate to be
    used in RF by setting oversampling ratio. Valid oversampling values are 1, 2,
    4, 8, 16, 32 or 0 (use device default oversampling value).
    :param rate: sampling rate in Hz to set
    :param oversample: RF oversampling ratio
    :return:  0 on success, (-1) on failure
    """
    LMS_SetSampleRate(_c_device, rate, oversample)

cpdef tuple get_sample_rate(bool dir_tx, size_t chan):
    """
    Get the sampling rate of the specified LMS device RX or TX channel.
    The function obtains the sample rate used in data interface with the host and
    the RF sample rate used by DAC/ADC.
    :param dir_tx: Select RX or TX
    :param chan: Channel index
    :return: tuple of host_Hz, rf_Hz or tuple -1,-1 on Error
    """
    cdef float_type host_hz = 0.0  # sampling rate used for data exchange with the host
    cdef float_type rf_hz = 0.0  # RF sampling rate in Hz

    result = LMS_GetSampleRate(_c_device, dir_tx, chan, &host_hz, &rf_hz)
    if result == 0:
        return host_hz, rf_hz
    else:
        return -1, -1

cpdef tuple get_sample_rate_range(bool dir_tx):
    """
    Get the range of supported sampling rates.
    :param dir_tx: Select RX or TX
    :return: Tuple (start, end, step) of Allowed sample rate range in Hz, (-1, -1, -1) on Error
    """
    cdef lms_range_t sample_rate_range
    result = LMS_GetSampleRateRange(_c_device, dir_tx, &sample_rate_range)
    if result == 0:
        return sample_rate_range.min, sample_rate_range.max, sample_rate_range.step
    else:
        return -1, -1, -1
