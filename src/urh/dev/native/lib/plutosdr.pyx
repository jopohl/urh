from cplutosdr cimport *

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

cpdef unsigned int get_device(str uri, unsigned int index=0):
    cdef iio_context *ctx = iio_create_context_from_uri(uri.encode())
    cdef iio_device* dev = iio_context_get_device(ctx, index)

    print("got device")
    name = iio_device_get_name(dev)

    print("got name")
    print(name.decode())

