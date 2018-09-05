from libc.stdint cimport uint8_t, uint16_t
from libcpp cimport bool

cdef extern from "libbladeRF.h":
    struct bladerf

    enum bladerf_backend:
        BLADERF_BACKEND_ANY,         # "Don't Care" -- use any available backend
        BLADERF_BACKEND_LINUX,       # Linux kernel driver
        BLADERF_BACKEND_LIBUSB,      # libusb
        BLADERF_BACKEND_CYPRESS,     # CyAPI
        BLADERF_BACKEND_DUMMY = 100, # Dummy used for development purposes

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
        BLADERF_MODULE_TX               # Transmit Module

    int bladerf_enable_module(bladerf *dev, bladerf_module m, bool enable)

    ctypedef int bladerf_channel

    bladerf_channel BLADERF_CHANNEL_RX(bladerf_channel ch)
    bladerf_channel BLADERF_CHANNEL_TX(bladerf_channel ch)
    bladerf_channel BLADERF_CHANNEL_INVALID()
    bool BLADERF_CHANNEL_IS_TX(bladerf_channel ch)

    ctypedef enum bladerf_direction:
        BLADERF_RX = 0
        BLADERF_TX = 1

    ctypedef enum bladerf_channel_layout:
        BLADERF_RX_X1 = 0
        BLADERF_TX_X1 = 1
        BLADERF_RX_X2 = 2
        BLADERF_TX_X2 = 3

    size_t bladerf_get_channel_count(bladerf *dev, bladerf_direction dir)
