from urh.dev.native.lib.cbladerf cimport *
from libcpp cimport bool

cdef bladerf* _c_device

cpdef int CHANNEL = 0
cpdef bool IS_TX = False

cpdef set_tx(bool is_tx):
    global IS_TX
    IS_TX = <bool>is_tx

cpdef bool get_tx():
    return IS_TX

cpdef set_channel(bladerf_channel channel):
    global CHANNEL
    CHANNEL = <bladerf_channel>channel
    return 0

cpdef bladerf_channel get_channel():
    return CHANNEL

cpdef bladerf_channel get_current_bladerf_channel():
    if IS_TX:
        return BLADERF_CHANNEL_TX(get_channel())
    else:
        return BLADERF_CHANNEL_RX(get_channel())

cpdef int enable_module():
    return bladerf_enable_module(_c_device, get_current_bladerf_channel(), True)

cpdef int disable_module():
    return bladerf_enable_module(_c_device, get_current_bladerf_channel(), False)

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

cpdef int set_gain(bladerf_gain gain):
    return bladerf_set_gain(_c_device, get_current_bladerf_channel(), gain)

cpdef int get_gain():
    cdef bladerf_gain result = 0

    err = bladerf_get_gain(_c_device, get_current_bladerf_channel(), &result)
    if err == 0:
        return result
    else:
        return -42

cpdef int set_sample_rate(bladerf_sample_rate sample_rate):
    return bladerf_set_sample_rate(_c_device, get_current_bladerf_channel(), sample_rate, NULL)

cpdef bladerf_sample_rate get_sample_rate():
    cdef bladerf_sample_rate result = 0
    err = bladerf_get_sample_rate(_c_device, get_current_bladerf_channel(), &result)
    if err != 0:
        return 0

    return result
