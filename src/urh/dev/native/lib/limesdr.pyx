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
