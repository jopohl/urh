import unittest

import numpy as np

from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class GFSK(unittest.TestCase):
    def test_plot(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "FSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 2e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3

        bits = "10101010101010101010101010101010100110100111110110011010011111011101001001100001011011010111101011101101100001100010011000101000111110110111101011010011001110010011000010100111010000111111110100011100111000010111010000100011101011010000110110111011111111011000001101011001110001101010001010111111001101001100001000011100001101000100101110010011110111101001000011101110110110000100011111010110111011011100010100100010000001001011101110010100001000111"
        bits = [True if b=="1" else False for b in bits]
        modulator.modulate(bits)
        modulator.modulated_samples.tofile("/tmp/test.complex")


    def test_gfsk(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "FSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3
        modulator.modulate([True, False, False, True, False], 9437)
        s = modulator.modulated_samples
        modulator.modulate([True, False, True], 9845) #, start=len(s))
        s = np.concatenate((s, modulator.modulated_samples))
        modulator.modulate([True, False, True, False], 8457) #, start=len(s))
        s = np.concatenate((s, modulator.modulated_samples))

        s.tofile("/tmp/test.complex")

        pa = ProtocolAnalyzer(Signal("/tmp/test.complex", "test", modulation="FSK"))
        pa.get_protocol_from_signal()



    def gauss(self, sigma=0.5, truncate=4.0):
        sd = float(sigma)
        # make the radius of the filter equal to truncate standard deviations
        lw = int(truncate * sd + 0.5)
        weights = [0.0] * (2 * lw + 1)
        weights[lw] = 1.0
        sum = 1.0
        sd = sd * sd
        # calculate the kernel:
        for ii in range(1, lw + 1):
            tmp = np.exp(-0.5 * float(ii * ii) / sd)
            weights[lw + ii] = tmp
            weights[lw - ii] = tmp
            sum += 2.0 * tmp
        for ii in range(2 * lw + 1):
            weights[ii] /= sum

        return weights

    def gauss2(self, n=11, sigma=1.0):
        r = range(-int(n / 2), int(n / 2) + 1)
        result =  np.array([1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-float(x) ** 2 / (2 * sigma ** 2)) for x in r])
        return result / result.sum()

    def gauss3(self, n=22, bt=0.5):
        a = (1/bt) * np.sqrt(np.log10(2)/2)
        r = range(-int(n / 2), int(n / 2) + 1)
        result =  np.array([np.sqrt(np.pi)/a * np.exp(-(np.pi ** 2 * x ** 2)/(a**2)) for x in r])
        return result / result.sum()



    def test_gnuradio_gauss(self):
        bit_len = 100
        gaussian_taps = self.firdes_gaussian(bit_len, 0.5, 4*bit_len)
        sqwave = (1,) * bit_len
        taps = np.convolve(np.array(gaussian_taps),np.array(sqwave))
        # modulator = Modulator("gfsk")
        # modulator.modulation_type_str = "FSK"
        # modulator.samples_per_bit = 100
        # modulator.sample_rate = 1e6
        # modulator.param_for_one = 20e3
        # modulator.param_for_zero = -10e3
        # modulator.modulate([True, False, False, True, False], 9437)
        # s = modulator.modulated_samples
        # modulator.modulate([True, False, True], 9845) #, start=len(s))
        # s = np.concatenate((s, modulator.modulated_samples))
        # modulator.modulate([True, False, True, False], 8457) #, start=len(s))
        # s = np.concatenate((s, modulator.modulated_samples))




    def firdes_gaussian(self, samples_per_symbol, bt, ntaps):
        taps = np.empty(ntaps, dtype=np.float32)
        dt = 1/samples_per_symbol
        s = 1.0/(np.sqrt(np.log(2.0)) / (2*np.pi*bt))
        t0 = -0.5 * ntaps
        for i in range(ntaps):
            t0 += 1
            ts = s*dt*t0
            taps[i] = np.exp(-0.5*ts*ts)

        taps /= taps.sum()
        return taps
