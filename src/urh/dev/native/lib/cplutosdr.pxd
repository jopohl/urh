from libcpp cimport bool

cdef extern from "iio.h":
    struct iio_context
    struct iio_device
    struct iio_channel
    struct iio_buffer

    struct iio_context_info
    struct iio_scan_context


    iio_scan_context * iio_create_scan_context(const char *backend, unsigned int flags)
    void iio_scan_context_destroy(iio_scan_context *ctx)
    ssize_t iio_scan_context_get_info_list(iio_scan_context *ctx, iio_context_info ***info)
    void iio_context_info_list_free(iio_context_info **info)
    const char * iio_context_info_get_description(const iio_context_info *info)
    const char * iio_context_info_get_uri(const iio_context_info *info)
    iio_device * iio_context_find_device(const iio_context *ctx, const char *name)
    void iio_context_destroy(iio_context *ctx)

    iio_context* iio_create_default_context()
    iio_context * iio_create_context_from_uri(const char *uri)
    unsigned int iio_context_get_devices_count(const iio_context *ctx)
    iio_device* iio_context_get_device(iio_context *ctx, unsigned int index)
    iio_buffer * iio_device_create_buffer(const iio_device *dev, size_t samples_count, bool cyclic)
    void iio_buffer_destroy(iio_buffer *buf)
    ssize_t iio_buffer_refill(iio_buffer *buf)
    ssize_t iio_buffer_step(const iio_buffer *buf)
    void * iio_buffer_first(const iio_buffer *buf, const iio_channel *chn)
    void * iio_buffer_end(const iio_buffer *buf)
    ssize_t iio_buffer_push(iio_buffer *buf)

    const char * iio_device_get_name(const iio_device *dev)
    iio_channel * iio_device_find_channel(const iio_device *dev, const char *name, bool output)
    unsigned int iio_device_get_channels_count(const iio_device *dev)
    iio_channel* iio_device_get_channel(const iio_device *dev, unsigned int index)

    const char * iio_channel_get_id(const iio_channel *chn)
    const char * iio_channel_get_name(const iio_channel *chn)
    bool iio_channel_is_output(const iio_channel *chn)
    void iio_channel_enable(iio_channel *chn)
    void iio_channel_disable(iio_channel *chn)
    bool iio_channel_is_enabled(iio_channel *chn)
    int iio_channel_attr_write_longlong(const iio_channel *chn, const char *attr, long long val)
    int iio_channel_attr_write_double(const iio_channel *chn, const char *attr, double val)
    ssize_t iio_channel_attr_write(const iio_channel *chn, const char *attr, const char *src)

