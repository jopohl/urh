from libcpp cimport bool

cdef extern from "lime/LimeSuite.h":
    ctypedef void lms_device_t
    ctypedef char lms_info_str_t[256]

    int LMS_GetDeviceList(lms_info_str_t *dev_list)
    int LMS_Open(lms_device_t ** device, lms_info_str_t info, void*args)
    int LMS_Close(lms_device_t *device)
    int LMS_Disconnect(lms_device_t *device)
    bool LMS_IsOpen(lms_device_t *device, int port)
