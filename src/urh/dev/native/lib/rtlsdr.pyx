cimport crtlsdr
from libc.stdlib cimport malloc

ctypedef unsigned char uint8_t
ctypedef unsigned short uint16_t
ctypedef unsigned int  uint32_t
ctypedef unsigned long long uint64_t

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
