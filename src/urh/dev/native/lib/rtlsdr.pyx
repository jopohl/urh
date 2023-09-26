cimport urh.dev.native.lib.crtlsdr as crtlsdr
from libc.stdlib cimport malloc, free

ctypedef unsigned char uint8_t
ctypedef unsigned short uint16_t
ctypedef unsigned int  uint32_t
ctypedef unsigned long long uint64_t

cdef crtlsdr.rtlsdr_dev_t*_c_device

cdef void _c_callback_recv(unsigned char *buffer, uint32_t length, void *ctx) noexcept:
    global f
    conn = <object> ctx
    (<object>f)(buffer[0:length])


IF RTLSDR_BANDWIDTH_SUPPORT == 1:
    cpdef bandwidth_is_adjustable():
        return True
    cpdef int set_tuner_bandwidth(uint32_t bw):
        """
        Set the bandwidth for the device.
    
        :param bw: bandwidth in Hz. Zero means automatic BW selection.
        :return 0 on success
        """
        return crtlsdr.rtlsdr_set_tuner_bandwidth(_c_device, bw)
ELSE:
    cpdef bandwidth_is_adjustable():
        return False
    cpdef int set_tuner_bandwidth(uint32_t bw):
        return -100

cpdef uint32_t get_device_count():
    return crtlsdr.rtlsdr_get_device_count()

cpdef str get_device_name(uint32_t index):
    return crtlsdr.rtlsdr_get_device_name(index).decode('UTF-8')

cpdef tuple get_device_usb_strings(uint32_t index):
    """

    :param index: index of the device
    :return: manufacturer name, product name, serial serial number on success else None, None, None
    """
    cdef char *manufacturer = <char *> malloc(256 * sizeof(char))
    cdef char *product = <char *> malloc(256 * sizeof(char))
    cdef char *serial = <char *> malloc(256 * sizeof(char))
    result = crtlsdr.rtlsdr_get_device_usb_strings(index, manufacturer, product, serial)
    try:
        if result == 0:
            return manufacturer.decode('UTF-8'), product.decode('UTF-8'), serial.decode('UTF-8')
        else:
            return None, None, None
    finally:
        free(manufacturer)
        free(product)
        free(serial)

cpdef int get_index_by_serial(str serial):
    """
    Get device index by USB serial string descriptor.

    :param serial: serial string of the device
    :return: device index of first device where the name matched
             -1 if name is NULL
             -2 if no devices were found at all
             -3 if devices were found, but none with matching name
    """
    serial_byte_string = serial.encode('UTF-8')
    return crtlsdr.rtlsdr_get_index_by_serial(<char *> serial_byte_string)

cpdef list get_device_list():
    result = []
    cdef uint32_t i, n = get_device_count()
    for i in range(n):
        manufacturer, product, serial = get_device_usb_strings(i)
        result.append("{} {} (SN: {})".format(manufacturer, product, serial))
    return result

cpdef int open(uint32_t index):
    return crtlsdr.rtlsdr_open(&_c_device, index)

cpdef int close():
    return crtlsdr.rtlsdr_close(_c_device)

cpdef int set_xtal_freq(uint32_t rtl_freq, uint32_t tuner_freq):
    """
     Set crystal oscillator frequencies used for the RTL2832 and the tuner IC.

    Usually both ICs use the same clock. Changing the clock may make sense if
    you are applying an external clock to the tuner or to compensate the
    frequency (and samplerate) error caused by the original (cheap) crystal.

    NOTE: Call this function only if you fully understand the implications.

    :param rtl_freq: frequency value used to clock the RTL2832 in Hz
    :param tuner_freq: frequency value used to clock the tuner IC in Hz
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_xtal_freq(_c_device, rtl_freq, tuner_freq)

cpdef tuple get_xtal_freq():
    """
    Get crystal oscillator frequencies used for the RTL2832 and the tuner IC.
    Usually both ICs use the same clock.

    :return: rtl_freq frequency value used to clock the RTL2832 in Hz,
             tuner_freq frequency value used to clock the tuner IC in Hz
    """
    cdef uint32_t rtl_freq = 0
    cdef uint32_t tuner_freq = 0
    result = crtlsdr.rtlsdr_get_xtal_freq(_c_device, &rtl_freq, &tuner_freq)

    if result == 0:
        return rtl_freq, tuner_freq
    else:
        return None, None

cpdef tuple get_usb_strings():
    cdef char *manufacturer = <char *> malloc(256 * sizeof(char))
    cdef char *product = <char *> malloc(256 * sizeof(char))
    cdef char *serial = <char *> malloc(256 * sizeof(char))
    result = crtlsdr.rtlsdr_get_usb_strings(_c_device, manufacturer, product, serial)
    if result == 0:
        return manufacturer.decode('UTF-8'), product.decode('UTF-8'), serial.decode('UTF-8')
    else:
        return None, None, None

cpdef int set_center_freq(uint32_t freq):
    return crtlsdr.rtlsdr_set_center_freq(_c_device, freq)

cpdef uint32_t get_center_freq():
    """
    Get actual frequency the device is tuned to.

    :return: 0 on error, frequency in Hz otherwise
    """
    return crtlsdr.rtlsdr_get_center_freq(_c_device)

cpdef int set_freq_correction(int ppm):
    """
    Set the frequency correction value for the device.

    :param ppm: ppm correction value in parts per million (ppm)
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_freq_correction(_c_device, ppm)

cpdef int get_freq_correction():
    """
    Get actual frequency correction value of the device.

    :return: correction value in parts per million (ppm)
    """
    return crtlsdr.rtlsdr_get_freq_correction(_c_device)

cpdef crtlsdr.rtlsdr_tuner get_tuner_type():
    """
    Get the tuner type.

    :return: RTLSDR_TUNER_UNKNOWN on error, tuner type otherwise
    """
    return crtlsdr.rtlsdr_get_tuner_type(_c_device)

cpdef list get_tuner_gains():
    """
    Get a list of gains supported by the tuner.
    NOTE: The gains argument must be preallocated by the caller. If NULL is
    being given instead, the number of available gain values will be returned.

    :return: gains array of gain values. In tenths of a dB, 115 means 11.5 dB.
    """
    cdef int num_gains = crtlsdr.rtlsdr_get_tuner_gains(_c_device, NULL)
    if num_gains < 0:
        return None

    cdef int*gains = <int *> malloc(num_gains * sizeof(int))
    crtlsdr.rtlsdr_get_tuner_gains(_c_device, gains)

    try:
        return [gains[i] for i in range(num_gains)]
    finally:
        free(gains)

cpdef int set_tuner_gain(int gain):
    """
    Set the gain for the device.
    Manual gain mode must be enabled for this to work.

    Valid gain values (in tenths of a dB) for the E4000 tuner:
    -10, 15, 40, 65, 90, 115, 140, 165, 190,
    215, 240, 290, 340, 420, 430, 450, 470, 490

    Valid gain values may be queried with rtlsdr_get_tuner_gains function.

    :param gain: gain in tenths of a dB, 115 means 11.5 dB.
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_tuner_gain(_c_device, gain)

cpdef int get_tuner_gain():
    """
    Get actual gain the device is configured to.

    :return: 0 on error, gain in tenths of a dB, 115 means 11.5 dB.
    """
    return crtlsdr.rtlsdr_get_tuner_gain(_c_device)

cpdef int set_tuner_if_gain(int stage, int gain):
    """
    Set the intermediate frequency gain for the device.

    :param stage: intermediate frequency gain stage number (1 to 6 for E4000)
    :param gain: in tenths of a dB, -30 means -3.0 dB.
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_tuner_if_gain(_c_device, stage, gain)

cpdef int set_tuner_gain_mode(int manual):
    """
    Set the gain mode (automatic/manual) for the device.
    Manual gain mode must be enabled for the gain setter function to work.

    :param manual: 1 means manual gain mode shall be enabled.
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_tuner_gain_mode(_c_device, manual)

cpdef int set_sample_rate(uint32_t sample_rate):
    """
    Set the sample rate for the device, also selects the baseband filters
    according to the requested sample rate for tuners where this is possible.

    :param sample_rate: the sample rate to be set, possible values are:
                225001 - 300000 Hz
  		        900001 - 3200000 Hz
  		        sample loss is to be expected for rates > 2400000
    :return:
    """
    return crtlsdr.rtlsdr_set_sample_rate(_c_device, sample_rate)

cpdef uint32_t get_sample_rate():
    """
    Get actual sample rate the device is configured to.
    :return: 0 on error, sample rate in Hz otherwise
    """
    return crtlsdr.rtlsdr_get_sample_rate(_c_device)

cpdef int set_agc_mode(int on):
    """
    Enable or disable the internal digital Automatic Gain Control of the RTL2832.

    :param on: digital AGC mode, 1 means enabled, 0 disabled
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_agc_mode(_c_device, on)

cpdef int set_direct_sampling(int on):
    """
    Enable or disable the direct sampling mode. When enabled, the IF mode
    of the RTL2832 is activated, and rtlsdr_set_center_freq() will control
    the IF-frequency of the DDC, which can be used to tune from 0 to 28.8 MHz
    (xtal frequency of the RTL2832).

    :param on: 0 means disabled, 1 I-ADC input enabled, 2 Q-ADC input enabled
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_direct_sampling(_c_device, on)

cpdef int get_direct_sampling():
    """
    Get state of the direct sampling mode

    :return: -1 on error, 0 means disabled, 1 I-ADC input enabled, 2 Q-ADC input enabled
    """
    return crtlsdr.rtlsdr_get_direct_sampling(_c_device)

cpdef int set_offset_tuning(int on):
    """
    Enable or disable offset tuning for zero-IF tuners, which allows to avoid
    problems caused by the DC offset of the ADCs and 1/f noise.

    :param on: 0 means disabled, 1 enabled
    :return: 0 on success
    """
    return crtlsdr.rtlsdr_set_offset_tuning(_c_device, on)

cpdef int get_offset_tuning():
    """
    Get state of the offset tuning mode

    :return: -1 on error, 0 means disabled, 1 enabled
    """
    return crtlsdr.rtlsdr_get_offset_tuning(_c_device)

cpdef int reset_buffer():
    return crtlsdr.rtlsdr_reset_buffer(_c_device)

cpdef bytes read_sync(int num_samples=8 * 32 * 512):
    """
    The raw, captured IQ data is 8 bit unsigned data.

    :return:
    """
    cdef uint8_t *samples = <uint8_t *> malloc(2*num_samples * sizeof(uint8_t))
    if not samples:
        raise MemoryError()

    cdef int n_read = 0
    try:
        crtlsdr.rtlsdr_read_sync(_c_device, <void *>samples, num_samples, &n_read)
        return bytes(samples[0:n_read])
    finally:
        free(samples)

cpdef int read_async(callback, connection):
    """
    Read samples from the device asynchronously. This function will block until
    it is being canceled using rtlsdr_cancel_async()
    read_bytes_async
    :return: 0 on success
    """
    global f
    f = callback
    return crtlsdr.rtlsdr_read_async(_c_device, _c_callback_recv, <void *>connection, 0, 0)

cpdef int cancel_async():
    """
    Cancel all pending asynchronous operations on the device.

    :return: 0 on success
    """
    return crtlsdr.rtlsdr_cancel_async(_c_device)

cpdef int set_bias_tee(int on):
    """
    Enable or disable the bias tee on GPIO PIN 0.
 
    return -1 if device is not initialized. 0 otherwise.
    """
    return crtlsdr.rtlsdr_set_bias_tee (_c_device, on)
