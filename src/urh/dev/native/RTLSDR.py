import numpy as np
import time

from urh.dev.native.lib import rtlsdr

class RTLSDR(object):
    def __init__(self):
        pass

    def unpack_complex(self, buffer, nvalues: int):
        """
        The raw, captured IQ data is 8 bit unsigned data.

        :return:
        """
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        result.real = (unpacked['r'] / 127.5) - 1.0
        result.imag = (unpacked['i'] / 127.5) - 1.0
        return result

if __name__ == "__main__":
    #recv_buffer = np.empty(16 * 32 * 512, dtype=np.complex64)
    from multiprocessing import Queue

    queue = Queue()
    def callback_recv(buffer):
        try:
            queue.put(buffer)
        except BrokenPipeError:
            pass
        return 0

    print("Device count:", rtlsdr.get_device_count())
    print("Device name:", rtlsdr.get_device_name(0))
    manufact, product, serial = rtlsdr.get_device_usb_strings(0)
    print("Manufacturer:", manufact)
    print("Product:", product)
    print("Serial", serial)
    print("Index by serial", rtlsdr.get_index_by_serial(serial))
    print("Open:", rtlsdr.open(0))
    print("Reset Buffer:", rtlsdr.reset_buffer())   # IMPORTANT
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
    print("Sample Rate", rtlsdr.get_sample_rate())
    print("Set Sample Rate to 300k", rtlsdr.set_sample_rate(300*10**3))
    print("Sample Rate", rtlsdr.get_sample_rate())
    read_samples = rtlsdr.read_sync(1024)
    print(read_samples)
    print(RTLSDR().unpack_complex(read_samples, len(read_samples) // 2))
    #print("Read async:", rtlsdr.read_async(callback_recv))
    #time.sleep(5)
    #rtlsdr.cancel_async()
    #print(queue)

    #iq = np.empty(len(bytes) // 2, 'complex')
    #iq.real, iq.imag = bytes[::2], bytes[1::2]
    #iq /= (255 / 2)
    #iq -= (1 + 1j)

    print("Close:", rtlsdr.close())
