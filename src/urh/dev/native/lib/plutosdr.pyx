from cplutosdr cimport *
from libc.stdint cimport int16_t

from libc.stdlib cimport malloc, free
cdef iio_context* _c_context


cdef iio_buffer* _rx_buffer

cdef bool IS_TX = True
cdef size_t RX_BUFFER_SIZE = 4096

cpdef set_tx(bool is_tx):
    global IS_TX
    IS_TX = <bool>is_tx

cpdef bool get_tx():
    return IS_TX

cpdef tuple scan_devices():
    cdef iio_scan_context* ctx = iio_create_scan_context(NULL, 0)

    cdef iio_context_info** infos
    cdef ssize_t num_devices = iio_scan_context_get_info_list(ctx, &infos)

    cdef list descs = []
    cdef list uris = []
    for i in range(0, num_devices):
        desc = iio_context_info_get_description(infos[0])
        uri = iio_context_info_get_uri(infos[0])
        descs.append(desc.decode())
        uris.append(uri.decode())

    iio_context_info_list_free(infos)
    iio_scan_context_destroy(ctx)

    return descs, uris

cpdef int set_center_freq(long long center_freq):
    cdef iio_device* phy = iio_context_find_device(_c_context, "ad9361-phy")
    if IS_TX:
        return iio_channel_attr_write_longlong(iio_device_find_channel(phy, "altvoltage1", True), "frequency", center_freq)
    else:
        return iio_channel_attr_write_longlong(iio_device_find_channel(phy, "altvoltage0", True), "frequency", center_freq)

cpdef int set_sample_rate(long long sample_rate):
    cdef iio_device* phy = iio_context_find_device(_c_context, "ad9361-phy")
    return iio_channel_attr_write_longlong(iio_device_find_channel(phy, "voltage0", IS_TX), "sampling_frequency", sample_rate)

cpdef int set_bandwidth(long long bandwidth):
    cdef iio_device* phy = iio_context_find_device(_c_context, "ad9361-phy")
    return iio_channel_attr_write_longlong(iio_device_find_channel(phy, "voltage0", IS_TX), "rf_bandwidth", bandwidth)


cpdef int set_rf_gain(long long gain):
    cdef iio_device* phy = iio_context_find_device(_c_context, "ad9361-phy")
    iio_channel_attr_write(iio_device_find_channel(phy, "voltage0", IS_TX), "gain_control_mode", "manual")
    return iio_channel_attr_write_longlong(iio_device_find_channel(phy, "voltage0", IS_TX), "hardwaregain", gain)

cpdef int open(str uri):
    global _c_context
    _c_context = iio_create_context_from_uri(uri.encode())

    if _c_context != NULL:
        return 0
    else:
        return -1

cpdef int setup_rx():
    dev = iio_context_find_device(_c_context, "cf-ad9361-lpc")
    set_rx_channels_status(enable=True)
    global _rx_buffer
    _rx_buffer = iio_device_create_buffer(dev, RX_BUFFER_SIZE, False)
    return 0

cpdef bytes receive_sync(connection):
    cdef void *p_dat
    cdef void *p_end
    cdef ssize_t p_inc
    cdef int16_t i, q
    cdef iio_device* dev = iio_context_find_device(_c_context, "cf-ad9361-lpc")

    iio_buffer_refill(_rx_buffer)

    p_inc = iio_buffer_step(_rx_buffer)
    p_end = iio_buffer_end(_rx_buffer)

    chan = iio_device_find_channel(dev, "voltage0", 0)
    p_dat = iio_buffer_first(_rx_buffer, chan)

    cdef int16_t *samples = <int16_t *> malloc(2*RX_BUFFER_SIZE * sizeof(int16_t))
    cdef unsigned int index = 0

    try:
        while p_dat < p_end:
            i = (<int16_t*>p_dat)[0]
            q = (<int16_t*>p_dat)[1]

            samples[index] = i
            samples[index+1] = q
            index += 2
            p_dat += p_inc

        connection.send_bytes(<int16_t [:2*RX_BUFFER_SIZE]>samples)
    finally:
        free(samples)


cpdef stop_rx():
    set_rx_channels_status(enable=False)
    iio_buffer_destroy(_rx_buffer)
    return 0

cpdef stop_tx():
    raise NotImplementedError("todo")

cpdef int close():
    if IS_TX:
        return stop_tx()
    else:
        return stop_rx()

cpdef set_rx_channels_status(bool enable):
    cdef iio_channel *rx0_i
    cdef iio_channel *rx0_q
    cdef iio_device* dev = iio_context_find_device(_c_context, "cf-ad9361-lpc")
    rx0_i = iio_device_find_channel(dev, "voltage0", 0)
    rx0_q = iio_device_find_channel(dev, "voltage1", 0)

    if enable:
        iio_channel_enable(rx0_i)
        iio_channel_enable(rx0_q)
    else:
        iio_channel_disable(rx0_i)
        iio_channel_disable(rx0_q)


