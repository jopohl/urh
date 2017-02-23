
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
    print("Open:", rtlsdr.open(0))
    print("XTAL Freq:", rtlsdr.get_xtal_freq())
    print("USB device strings", rtlsdr.get_usb_strings())
    print("Center Freq:", rtlsdr.get_center_freq())
    print("Set center freq to 433MHz", rtlsdr.set_center_freq(int(433e6)))
    print("Center Freq:", rtlsdr.get_center_freq())
    print("Freq Correction", rtlsdr.get_freq_correction())
    print("Set Freq Correction to 10", rtlsdr.set_freq_correction(10))
    print("Freq Correction", rtlsdr.get_freq_correction())
    print("tuner type", rtlsdr.get_tuner_type())
    print("tuner_gains", rtlsdr.get_tuner_gains())
    print("set_manual_gain_mode", rtlsdr.set_tuner_gain_mode(1))
    print("tuner gain", rtlsdr.get_tuner_gain())
    print("set gain to 338", rtlsdr.set_tuner_gain(338))
    print("tuner gain", rtlsdr.get_tuner_gain())
    print("set tuner if gain", rtlsdr.set_tuner_if_gain(1, 10))
    print("Close:", rtlsdr.close())
