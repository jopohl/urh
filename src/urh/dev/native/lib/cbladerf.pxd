from libc.stdint cimport uint8_t, uint16_t
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

    struct bladerf_version:
        uint16_t major
        uint16_t minor
        uint16_t patch
        const char* describe

    int bladerf_get_serial(bladerf *dev, char *serial)

    ctypedef enum bladerf_module:
        BLADERF_MODULE_INVALID = -1    # Invalid module entry
        BLADERF_MODULE_RX              # Receive Module
        BLADERF_MODULE_TX              # Transmit Module


    ctypedef int bladerf_channel
    int bladerf_enable_module(bladerf *dev, bladerf_channel ch, bool enable)

    bladerf_channel BLADERF_CHANNEL_RX(bladerf_channel ch)
    bladerf_channel BLADERF_CHANNEL_TX(bladerf_channel ch)
    bladerf_channel BLADERF_CHANNEL_INVALID()
    bool BLADERF_CHANNEL_IS_TX(bladerf_channel ch)

    ctypedef enum bladerf_direction:
        BLADERF_RX = 0
        BLADERF_TX = 1

    ctypedef enum bladerf_channel_layout:
        BLADERF_RX_X1 = 0  # x1 RX (SISO)
        BLADERF_TX_X1 = 1  # x1 TX (SISO
        BLADERF_RX_X2 = 2  # x2 RX (MIMO)
        BLADERF_TX_X2 = 3  # x2 TX (MIMO)

    size_t bladerf_get_channel_count(bladerf *dev, bladerf_direction dir)

    ctypedef int bladerf_gain

    ctypedef enum bladerf_gain_mode:
        BLADERF_GAIN_DEFAULT
        BLADERF_GAIN_MGC
        BLADERF_GAIN_FASTATTACK_AGC
        BLADERF_GAIN_SLOWATTACK_AGC
        BLADERF_GAIN_HYBRID_AGC

    int bladerf_set_gain(bladerf *dev, bladerf_channel ch, bladerf_gain gain)
    int bladerf_get_gain(bladerf *dev, bladerf_channel ch, bladerf_gain *gain)
    int bladerf_set_gain_mode(bladerf *dev, bladerf_channel ch, bladerf_gain_mode mode)
    int bladerf_get_gain_mode(bladerf *dev, bladerf_channel ch, bladerf_gain_mode *mode)

    ctypedef unsigned int bladerf_sample_rate

    int bladerf_set_sample_rate(bladerf *dev, bladerf_channel ch, bladerf_sample_rate rate, bladerf_sample_rate *actual)
    int bladerf_get_sample_rate(bladerf *dev, bladerf_channel ch, bladerf_sample_rate *rate)