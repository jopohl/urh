# cython wrapper for RTL-SDR (https://github.com/pinkavaj/rtl-sdr)

cimport crtlsdr
from libc.stdlib cimport malloc

ctypedef unsigned char uint8_t
ctypedef unsigned short uint16_t
ctypedef unsigned int  uint32_t
ctypedef unsigned long long uint64_t

cdef crtlsdr.rtlsdr_dev_t* _c_device

cpdef uint32_t get_device_count():
    return crtlsdr.rtlsdr_get_device_count()

cpdef str get_device_name(uint32_t index):
    return crtlsdr.rtlsdr_get_device_name(index).decode('UTF-8')

cpdef tuple get_device_usb_strings(uint32_t index):
    """

    :param index: index of the device
    :return: manufacturer name, product name, serial serial number on success else None, None, None
    """
    cdef char *manufacturer = <char *>malloc(256 * sizeof(char))
    cdef char *product = <char *>malloc(256 * sizeof(char))
    cdef char *serial = <char *>malloc(256 * sizeof(char))
    result = crtlsdr.rtlsdr_get_device_usb_strings(index, manufacturer, product, serial)
    if result == 0:
        return manufacturer.decode('UTF-8'), product.decode('UTF-8'), serial.decode('UTF-8')
    else:
        return None, None, None

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
    return crtlsdr.rtlsdr_get_index_by_serial(<char *>serial_byte_string)

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
    cdef char *manufacturer = <char *>malloc(256 * sizeof(char))
    cdef char *product = <char *>malloc(256 * sizeof(char))
    cdef char *serial = <char *>malloc(256 * sizeof(char))
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
