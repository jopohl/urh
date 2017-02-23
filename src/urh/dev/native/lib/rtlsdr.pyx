cimport crtlsdr

cpdef rtlsdr_get_device_count():
    return crtlsdr.rtlsdr_get_device_count()
