from cplutosdr cimport *
from libc.stdint cimport int16_t

from libc.stdlib cimport malloc, free
cdef iio_device* _c_device

cdef iio_channel *_rx0_i, *_rx0_q
cdef iio_buffer *_rx_buffer

cdef bool RX = True
cdef size_t RX_BUFFER_SIZE = 4096

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

cpdef int setup_rx(str uri):
    cdef iio_context *ctx = iio_create_context_from_uri(uri.encode())
    global _c_device
    _c_device = iio_context_find_device(ctx, "cf-ad9361-lpc")
    set_rx_channels_status(enable=True)

    global _rx_buffer
    _rx_buffer = iio_device_create_buffer(_c_device, RX_BUFFER_SIZE, False)
    if not _rx_buffer:
        return  -1
    return 0

cpdef bytes receive_sync():
    cdef void *p_dat
    cdef void *p_end
    cdef ssize_t p_inc
    cdef int16_t i, q

    iio_buffer_refill(_rx_buffer)

    p_inc = iio_buffer_step(_rx_buffer)
    p_end = iio_buffer_end(_rx_buffer)

    p_dat = iio_buffer_first(_rx_buffer, _rx0_i)

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

        return bytes(<int16_t [:2*RX_BUFFER_SIZE]>samples)
    finally:
        free(samples)


cpdef stop_rx():
    iio_buffer_destroy(_rx_buffer)
    set_rx_channels_status(enable=False)
    return 0

cpdef set_rx_channels_status(bool enable):
    global _rx0_i, _rx0_q
    _rx0_i = iio_device_find_channel(_c_device, "voltage0", 0)
    _rx0_q = iio_device_find_channel(_c_device, "voltage1", 0)

    if enable:
        iio_channel_enable(_rx0_i)
        iio_channel_enable(_rx0_q)
    else:
        iio_channel_disable(_rx0_i)
        iio_channel_disable(_rx0_q)

cpdef setup(str uri):
    if RX:
        setup_rx(uri)


cpdef unsigned int get_channel_count():
    return iio_device_get_channels_count(_c_device)

