
from urh.dev.native.lib import rtlsdr

class RTLSDR(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    print(rtlsdr.rtlsdr_get_device_count())
