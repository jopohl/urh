from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from libcpp cimport bool

cdef extern from "libbladeRF.h":
    struct bladerf

    enum bladerf_backend:
        BLADERF_BACKEND_ANY         # "Don't Care" -- use any available backend
        BLADERF_BACKEND_LINUX       # Linux kernel driver
        BLADERF_BACKEND_LIBUSB      # libusb
        BLADERF_BACKEND_CYPRESS     # CyAPI
        BLADERF_BACKEND_DUMMY = 100 # Dummy used for development purposes

    struct bladerf_devinfo:
        bladerf_backend backend # Backend to use when connecting to device
        char serial[33]         # Device serial number string
        uint8_t usb_bus         # Bus # device is attached to
        uint8_t usb_addr        # Device address on bus
        unsigned int instance   # Device instance or ID

    int bladerf_get_device_list(bladerf_devinfo **devices)
    int bladerf_free_device_list(bladerf_devinfo *devices)

    int bladerf_open(bladerf **device, const char *device_identifier)
    void bladerf_close(bladerf *device)

    struct s_bladerf_version "bladerf_version":
        uint16_t major
        uint16_t minor
        uint16_t patch
        const char* describe

    void bladerf_version(s_bladerf_version *version)
    int bladerf_get_serial(bladerf *dev, char *serial)

    ctypedef enum bladerf_module:
        BLADERF_MODULE_INVALID = -1    # Invalid module entry
        BLADERF_MODULE_RX              # Receive Module
        BLADERF_MODULE_TX              # Transmit Module


    IF BLADERF_API_VERSION >= 1.91:
        ctypedef int bladerf_channel
        bladerf_channel BLADERF_CHANNEL_RX(bladerf_channel ch)
        bladerf_channel BLADERF_CHANNEL_TX(bladerf_channel ch)
        bladerf_channel BLADERF_CHANNEL_INVALID()
        bool BLADERF_CHANNEL_IS_TX(bladerf_channel ch)
        int bladerf_enable_module(bladerf *dev, bladerf_channel ch, bool enable)
    ELSE:
        int bladerf_enable_module(bladerf *dev, bladerf_module m, bool enable)



    ctypedef enum bladerf_direction:
        BLADERF_RX = 0
        BLADERF_TX = 1

    ctypedef enum bladerf_channel_layout:
        BLADERF_RX_X1 = 0  # x1 RX (SISO)
        BLADERF_TX_X1 = 1  # x1 TX (SISO
        BLADERF_RX_X2 = 2  # x2 RX (MIMO)
        BLADERF_TX_X2 = 3  # x2 TX (MIMO)

    IF BLADERF_API_VERSION >= 1.91:
        ctypedef enum bladerf_gain_mode:
            BLADERF_GAIN_DEFAULT
            BLADERF_GAIN_MGC
            BLADERF_GAIN_FASTATTACK_AGC
            BLADERF_GAIN_SLOWATTACK_AGC
            BLADERF_GAIN_HYBRID_AGC
    ELSE:
        ctypedef enum bladerf_gain_mode:
            BLADERF_GAIN_AUTOMATIC
            BLADERF_GAIN_MANUAL

    IF BLADERF_API_VERSION >= 1.91:
        int bladerf_set_gain(bladerf *dev, bladerf_channel ch, int gain)
        int bladerf_set_gain_mode(bladerf *dev, bladerf_channel ch, bladerf_gain_mode mode)
    ELSE:
        int bladerf_set_gain(bladerf *dev, bladerf_module mod, int gain)
        int bladerf_set_gain_mode(bladerf *dev, bladerf_module mod, bladerf_gain_mode mode)

    IF BLADERF_API_VERSION >= 1.91:
        int bladerf_set_sample_rate(bladerf *dev, bladerf_channel ch, unsigned int rate, unsigned int *actual)
        int bladerf_get_sample_rate(bladerf *dev, bladerf_channel ch, unsigned int  *rate)
    ELSE:
        int bladerf_set_sample_rate(bladerf *dev, bladerf_module module, unsigned int rate, unsigned int  *actual)
        int bladerf_get_sample_rate(bladerf *dev, bladerf_module module, unsigned int *rate)

    IF BLADERF_API_VERSION >= 1.91:
        int bladerf_set_bandwidth(bladerf *dev, bladerf_channel ch, unsigned int bandwidth, unsigned int *actual)
        int bladerf_get_bandwidth(bladerf *dev, bladerf_channel ch, unsigned int *bandwidth)
    ELSE:
        int bladerf_set_bandwidth(bladerf *dev, bladerf_module module, unsigned int bandwidth, unsigned int *actual)
        int bladerf_get_bandwidth(bladerf *dev, bladerf_module module, unsigned int *bandwidth)

    IF BLADERF_API_VERSION >= 2:
        int bladerf_set_frequency(bladerf *dev, bladerf_channel ch, uint64_t frequency)
        int bladerf_get_frequency(bladerf *dev, bladerf_channel ch, uint64_t *frequency)
    ELIF BLADERF_API_VERSION >= 1.91:
        int bladerf_set_frequency(bladerf *dev, bladerf_channel ch, unsigned int frequency)
        int bladerf_get_frequency(bladerf *dev, bladerf_channel ch, unsigned int *frequency)
    ELSE:
        int bladerf_set_frequency(bladerf *dev, bladerf_module module, unsigned int frequency)
        int bladerf_get_frequency(bladerf *dev, bladerf_module module, unsigned int *frequency)

    ctypedef enum bladerf_format:
        BLADERF_FORMAT_SC16_Q11
        BLADERF_FORMAT_SC16_Q11_META

    ctypedef uint64_t bladerf_timestamp

    struct bladerf_metadata:
        bladerf_timestamp timestamp
        uint32_t flags
        uint32_t status
        unsigned int actual_count
        uint8_t reserved[32]

    IF BLADERF_API_VERSION >= 1.91:
        int bladerf_sync_config(bladerf *dev, bladerf_channel_layout layout, bladerf_format format, unsigned int num_buffers, unsigned int buffer_size, unsigned int num_transfers, unsigned int stream_timeout)
    ELSE:
        int bladerf_sync_config(bladerf *dev, bladerf_module module, bladerf_format format, unsigned int num_buffers, unsigned int buffer_size, unsigned int num_transfers, unsigned int stream_timeout)

    int bladerf_sync_rx(bladerf *dev, void *samples, unsigned int num_samples, bladerf_metadata *metadata, unsigned int timeout_ms)
    int bladerf_sync_tx(bladerf *dev, const void *samples, unsigned int num_samples, bladerf_metadata *metadata, unsigned int timeout_ms)

IF BLADERF_API_VERSION >= 2:
    ctypedef uint64_t bladerf_frequency
ELSE:
    ctypedef unsigned int bladerf_frequency

ctypedef unsigned int bladerf_sample_rate
ctypedef unsigned int bladerf_bandwidth
ctypedef int bladerf_gain