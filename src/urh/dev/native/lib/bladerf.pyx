
from urh.dev.native.lib.cbladerf cimport *
from libc.stdint cimport int16_t
from libcpp cimport bool
from libc.stdlib cimport malloc, free

cdef bladerf* _c_device

cdef int CHANNEL = 0
cpdef bool IS_TX = False

cpdef set_tx(bool is_tx):
    global IS_TX
    IS_TX = <bool>is_tx

cpdef bool get_tx():
    return IS_TX

cpdef set_channel(int channel):
    global CHANNEL
    CHANNEL = <int>channel
    return 0

cpdef int get_channel():
    return CHANNEL

IF BLADERF_API_VERSION >= 1.91:
    cpdef int get_current_bladerf_channel():
        if IS_TX:
            return BLADERF_CHANNEL_TX(get_channel())
        else:
            return BLADERF_CHANNEL_RX(get_channel())
ELSE:
    cpdef bladerf_module get_current_bladerf_channel():
        if IS_TX:
            return BLADERF_MODULE_RX
        else:
            return BLADERF_MODULE_TX

IF BLADERF_API_VERSION >= 1.91:
    cpdef bladerf_channel_layout get_current_channel_layout():
        if get_channel() == 0:
            if IS_TX:
                return BLADERF_TX_X1
            else:
                return BLADERF_RX_X1
        else:
            if IS_TX:
                return BLADERF_TX_X2
            else:
                return BLADERF_RX_X2
ELSE:
    cpdef bladerf_module get_current_channel_layout():
        return get_current_bladerf_channel()

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
    # disable the module when done, otherwise some warnings when closing during RX/TX
    disable_module()
    bladerf_close(_c_device)

cpdef int set_gain(bladerf_gain gain):
    if not IS_TX:
        # set to manual mode in rx case
        set_gain_mode_to_manual()

    return bladerf_set_gain(_c_device, get_current_bladerf_channel(), gain)

cpdef int set_gain_mode_to_manual():
    IF BLADERF_API_VERSION >= 1.91:
        bladerf_set_gain_mode(_c_device, get_current_bladerf_channel(), BLADERF_GAIN_MGC)
    ELSE:
        bladerf_set_gain_mode(_c_device, get_current_bladerf_channel(), BLADERF_GAIN_MANUAL)

cpdef int set_sample_rate(bladerf_sample_rate sample_rate):
    return bladerf_set_sample_rate(_c_device, get_current_bladerf_channel(), sample_rate, NULL)

cpdef bladerf_sample_rate get_sample_rate():
    cdef bladerf_sample_rate result = 0
    err = bladerf_get_sample_rate(_c_device, get_current_bladerf_channel(), &result)
    if err != 0:
        return 0

    return result

cpdef int set_bandwidth(bladerf_bandwidth bandwidth):
    return bladerf_set_bandwidth(_c_device, get_current_bladerf_channel(), bandwidth, NULL)

cpdef bladerf_bandwidth get_bandwidth():
    cdef bladerf_bandwidth result = 0
    err = bladerf_get_bandwidth(_c_device, get_current_bladerf_channel(), &result)

    if err != 0:
        return 0

    return result

cpdef int set_center_freq(bladerf_frequency frequency):
    return bladerf_set_frequency(_c_device, get_current_bladerf_channel(), frequency)

cpdef bladerf_frequency get_center_freq():
    cdef bladerf_frequency result = 0
    err = bladerf_get_frequency(_c_device, get_current_bladerf_channel(), &result)

    if err != 0:
        return 0

    return result

cpdef int prepare_sync():
    enable_module()
    return bladerf_sync_config(_c_device, get_current_channel_layout(), BLADERF_FORMAT_SC16_Q11, 32, 2048, 16, 100)

cpdef int16_t[:] receive_sync(connection, unsigned int num_samples):
    cdef int16_t *samples = <int16_t *> malloc(2*num_samples * sizeof(int16_t))
    if not samples:
        raise MemoryError()

    try:
        bladerf_sync_rx(_c_device, <void *>samples, num_samples, NULL, 100)
        return connection.send_bytes(<int16_t [:2*num_samples]>samples)
    finally:
        free(samples)

cpdef int send_sync(int16_t[::1] samples):
    cdef unsigned int num_samples = len(samples) // 2
    return bladerf_sync_tx(_c_device, &samples[0], num_samples, NULL, 100)

cpdef float get_api_version():
    cdef s_bladerf_version result

    bladerf_version(&result)

    print(result.major)
    print(result.minor)
    print(result.patch)

    print(result.describe.decode())