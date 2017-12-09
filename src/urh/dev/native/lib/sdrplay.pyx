cimport csdrplay
from libc.stdlib cimport malloc, free

ctypedef csdrplay.mir_sdr_DeviceT device_type

cpdef float get_api_version():
    cdef float version = 0.0
    csdrplay.mir_sdr_ApiVersion(&version)
    return version

cpdef get_devices():
    cdef device_type *devs = <device_type*>malloc(256 * sizeof(device_type))
    cdef unsigned int num_devs = 0
    try:
        csdrplay.mir_sdr_GetDevices(devs, &num_devs, 256)

        result = []

        for i in range(num_devs):
            d = {"serial": devs[i].SerNo.decode("utf-8"), "device_ref": devs[i].DevNm.decode("utf-8"),
                 "hw_version": devs[i].hwVer, "available": devs[i].devAvail}
            result.append(d)

        return result
    finally:
        free(devs)