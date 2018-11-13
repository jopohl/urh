cdef extern from "iio.h":
    struct iio_context
    struct iio_device

    struct iio_context_info
    struct iio_scan_context


    iio_scan_context * iio_create_scan_context(const char *backend, unsigned int flags)
    void iio_scan_context_destroy(iio_scan_context *ctx)
    ssize_t iio_scan_context_get_info_list(iio_scan_context *ctx, iio_context_info ***info)
    void iio_context_info_list_free(iio_context_info **info)
    const char * iio_context_info_get_description(const iio_context_info *info)
    const char * iio_context_info_get_uri(const iio_context_info *info)

    iio_context* iio_create_default_context()
    iio_context * iio_create_context_from_uri(const char *uri)
    unsigned int iio_context_get_devices_count(const iio_context *ctx)
    iio_device* iio_context_get_device(iio_context *ctx, unsigned int index);

    const char * iio_device_get_name(const iio_device *dev)
