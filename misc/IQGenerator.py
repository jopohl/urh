import numpy as np

from misc.Plotter import Plotter


class IQGenerator(object):
    def __init__(self, f_baseband=10, f_s=1000, bits=[True, False, True, True, False, False]):
        self.f_baseband = f_baseband
        self.f_s = f_s
        self.t_s = 1 / f_s
        self.bits = bits
        self.samples_per_cycle = int(f_s / f_baseband) + 1
        self.bit_len = 3 * self.samples_per_cycle
        self.modulation = "PSK"
        self.carrier_samples = []
        self.nsamples = self.bit_len * len(bits)

    def modulate_iq(self, add_noise=False):
        pos = 0
        result = np.empty(self.nsamples, dtype=np.complex64)
        self.carrier_samples = np.empty(self.nsamples, dtype=np.complex64)
        for bit in self.bits:
            if self.modulation == "FSK":
                freq = self.f_baseband if bit else int(0.5 * self.f_baseband)
            else:
                freq = self.f_baseband

            if self.modulation == "ASK":
                a = 1 if bit else 0
            else:
                a = 1

            if self.modulation == "PSK":
                phi = 0 if bit else np.pi
            else:
                phi = 0

            result.real[pos:pos + self.bit_len] = a * np.cos(
                2 * np.pi * freq * self.t_s * np.arange(pos, pos + self.bit_len) + phi)
            result.imag[pos:pos + self.bit_len] = a * np.sin(
                2 * np.pi * freq * self.t_s * np.arange(pos, pos + self.bit_len) + phi)
            self.carrier_samples.real[pos:pos + self.bit_len] = np.cos(
                2 * np.pi * self.f_baseband * self.t_s * np.arange(pos, pos + self.bit_len))
            self.carrier_samples.imag[pos:pos + self.bit_len] = np.sin(
                2 * np.pi * self.f_baseband * self.t_s * np.arange(pos, pos + self.bit_len))
            pos += self.bit_len


        if add_noise:
            noise = np.random.normal(0, 0.1, self.nsamples)
            result.real = np.add(result.real, noise)
            result.imag = np.add(result.imag, noise)
            self.carrier_samples.real = np.add(self.carrier_samples.real, noise)
            self.carrier_samples.imag = np.add(self.carrier_samples.imag, noise)
        return result

    def gen_iq_from_passband(self):
        # Lyons, 457, nur zu Dokuzwecken
        f_carrier = 433e6
        signal = np.sin(2 * np.pi * f_carrier * self.t_s * np.arange(0, self.nsamples))
        result = np.empty(self.nsamples, dtype=np.complex64)
        result.real = signal * np.cos(2 * np.pi * self.f_baseband * self.t_s * np.arange(0, self.nsamples))
        result.imag = signal * np.sin(2 * np.pi * self.f_baseband * self.t_s * np.arange(0, self.nsamples))
        result = self.lowpass(result,
                              self.f_baseband)  # Bei 2*f_c wird noch eine Frequenz angelegt, die schneiden wir hier weg
        return result

    def lowpass(self, data, cutoff):
        freq = np.fft.fftfreq(len(data), self.t_s)
        fft = np.fft.fft(data)
        fft_filtered = [fft[i] if abs(freq[i]) < cutoff else 0.0 for i in range(len(freq))]
        inverse = np.fft.ifft(fft_filtered)
        return inverse

    def get_spectrum(self, signal):
        w = np.abs(np.fft.fft(signal))
        freqs = np.fft.fftfreq(len(w), self.t_s)
        idx = np.argsort(freqs)
        return freqs[idx], w[idx]

    def get_max_freq(self, signal):
        w = np.abs(np.fft.fft(signal))
        freqs = np.fft.fftfreq(len(w))
        idx = np.argsort(w)
        return freqs[idx]

    def get_norm_angle(self, c):
        return np.arctan2(c.imag, c.real) + np.pi

    def costa_alpha_beta(self, bw, damp=(1 / np.sqrt(2))):
        # BW in range((2pi/200), (2pi/100))
        alpha = (4 * damp * bw) / (1 + 2 * damp * bw + bw * bw)
        beta = (4 * bw * bw) / (1 + 2 * damp * bw + bw * bw)

        return alpha, beta


    def psk_demod(self, iq_data):
        result = []
        nco_out = 0
        nco_times_sample = 0
        phase_error = 0
        modulus = 2 * np.pi
        costa_phase = 0
        costa_freq = 0
        lowpass_filtered = costa_freq

        # bw = (2 * np.pi / 100 + 2 * np.pi / 200) / 2
        bw = 2 * np.pi / 100
        alpha, beta = self.costa_alpha_beta(bw)

        freqs = []
        F = (np.arctan2(iq_data[1].imag, iq_data[1].real)) - (np.arctan2(iq_data[0].imag, iq_data[0].real))
        prod = 0
        avg_prod = -100

        N = 15
        lowpass_values = []

        for i in range(1, len(iq_data)):
            sample = iq_data[i]
            tmp = iq_data[i - 1].conjugate() * sample
            F = np.arctan2(tmp.imag, tmp.real)

            # # NCO Output
            nco_out = np.exp(-costa_phase * 1j)
            # # Sample * nco_out
            nco_times_sample = nco_out * sample
            # # LPF
            lowpass_filtered = nco_times_sample
            #
            #phase_error = np.arctan2(lowpass_filtered.imag, lowpass_filtered.real) # Arctan2 geht hier nicht, da durch Fehler in der Gleitkommarithmethik Teilweise -Pi statt 0 als Fehler ausgegeben wird. Das fuckt alles ab.
            # #phase_error = np.arctan2(nco_times_sample.imag, nco_times_sample.real)
            phase_error = lowpass_filtered.imag * lowpass_filtered.real

            costa_freq += beta * phase_error
            costa_phase += costa_freq + alpha * phase_error
            result.append(nco_times_sample.real)

        return result


    def get_angle(self, summed_angle):
        while summed_angle > np.pi:
            summed_angle -= np.pi
        return summed_angle


if __name__ == "__main__":
    iqg = IQGenerator()

    iq_data = iqg.modulate_iq(add_noise=True)
    # print("\n".join(map(str, iqg.psk_demod(iq_data))))
    demod = iqg.psk_demod(iq_data)
    # Plotter.generic_plot(np.arange(0, len(iq_data.real)), iq_data.real, iqg.modulation)
    carrier_plot = np.arange(0, len(iqg.carrier_samples)), iqg.carrier_samples.real, "Carrier"
    demod_plot = np.arange(0, len(demod)), demod, "Demod"
    # plot = carrier_plot + demod_plot
    plot = demod_plot

    Plotter.generic_plot(*plot)
    iq_data.tofile("../tests/data/psk_gen_noisy.complex")

    # x_range = np.arange(0, len(iq_data))
    # polar_discr = signalFunctions.quadrature_demod(iq_data, 0)
    # polar_discr[0] = 0
    # resulting_data_bits, pauses, resulting_bit_sample_positions = signalFunctions.get_protocol(polar_discr, 0.5, 3,
    #                                                                                            iqg.bit_len, 0, [])
    # print(resulting_data_bits)
    # Plotter.generic_plot(x_range, polar_discr, "Polar")
    # Plotter.generic_plot(x_range, iq_data.real, "I,"+iqg.modulation)
