from urh.dev.native.lib.cbladerf cimport *
from libcpp cimport bool

cdef bladerf* _c_device

cpdef list get_device_list():
    cdef bladerf_devinfo* dev_list
    cdef int i, num_devices
    num_devices = bladerf_get_device_list(&dev_list)

    if num_devices <= 0:
        return []

    result = []
    for i in range(0, num_devices):
        result.append(dev_list[i].serial.decode('utf-8'))

    bladerf_free_device_list(dev_list)
    return result

cpdef int open(str serial=""):
    cdef char* arg
    if serial == "":
        # Open first available
        return bladerf_open(&_c_device, NULL)
    else:
        argument_str = "*:serial={}".format(serial).encode('UTF-8')
        arg = <char*> argument_str
        return bladerf_open(&_c_device, arg)

cpdef void close():
    bladerf_close(_c_device)

cpdef size_t get_channel_count(bool tx):
    if tx:
        return bladerf_get_channel_count(_c_device, BLADERF_TX)
    else:
        return bladerf_get_channel_count(_c_device, BLADERF_RX)