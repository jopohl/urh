
from urh.dev.native.lib import rtlsdr

class RTLSDR(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    print("Device count:", rtlsdr.get_device_count())
    print("Device name:", rtlsdr.get_device_name(0))
    manufact, product, serial = rtlsdr.get_device_usb_strings(0)
    print("Manufacturer:", manufact)
    print("Product:", product)
    print("Serial", serial)
    print("Index by serial", rtlsdr.get_index_by_serial(serial))
