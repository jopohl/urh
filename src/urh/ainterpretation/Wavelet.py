import numpy as np

from urh.cythonext import auto_interpretation as  cy_auto_interpretation
from urh.signalprocessing.Modulator import Modulator


def normalized_haar_wavelet(omega, scale):
    omega_cpy = omega[:] / scale
    omega_cpy[0] = 1.0  # first element always zero, so prevent division by zero later

    result = (1j * np.square(-1 + np.exp(0.5j * omega))) / omega_cpy
    return result


def cwt_haar(x: np.ndarray, scale=10):
    """
    continuous haar wavelet transform based on the paper
    "A practical guide to wavelet analysis" by Christopher Torrence and Gilbert P Compo

    """
    next_power_two = 2 ** int(np.log2(len(x)))

    x = x[0:next_power_two]
    num_data = len(x)

    # get FFT of x (eq. (3) in paper)
    x_hat = np.fft.fft(x)

    # Get omega (eq. (5) in paper)
    f = (2.0 * np.pi / num_data)
    omega = f * np.concatenate((np.arange(0, num_data // 2), np.arange(num_data // 2, num_data) * -1))

    # get psi hat (eq. (6) in paper)
    psi_hat = np.sqrt(2.0 * np.pi * scale) * normalized_haar_wavelet(scale * omega, scale)

    # get W (eq. (4) in paper)
    W = np.fft.ifft(x_hat * psi_hat)

    return W[2 * scale:-2 * scale]


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    # data = np.fromfile("/home/joe/GIT/urh/tests/data/fsk.complex", dtype=np.complex64)[5:15000]
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask.complex", dtype=np.complex64)[462:754]
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/enocean.complex", dtype=np.complex64)[9724:10228]
    data = np.fromfile("/home/joe/GIT/publications/ainterpretation/experiments/signals/esaver_test4on.complex",
                       dtype=np.complex64)[86452:115541]

    # data = np.fromfile("/home/joe/GIT/urh/tests/data/action_ook.complex", dtype=np.complex64)[3780:4300]

    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask50.complex", dtype=np.complex64)
    # Wavelet transform the data
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask.complex", dtype=np.complex64)[0:2 ** 13]

    # data = np.fromfile("/tmp/generated.complex", dtype=np.complex64)

    # data = np.fromfile("/tmp/psk.complex", dtype=np.complex64)
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/psk_generated.complex", dtype=np.complex64)[0:8000]
    modulator = Modulator("")
    modulator.modulation_type_str = "PSK"
    modulator.param_for_zero = 0
    modulator.param_for_one = 180
    modulator.carrier_freq_hz = 5e3
    modulator.sample_rate = 200e3
    # data = modulator.modulate("1010", pause=0)

    # data = np.fromfile("/tmp/ask25.complex", dtype=np.complex64)
    # data = np.fromfile("/tmp/ask1080.complex", dtype=np.complex64)

    scale = 4
    median_filter_order = 11
    data = data[np.abs(data) > 0]

    # Normalize with max of data to prevent increasing variance for signals with lower amplitude
    data = data / np.abs(np.max(data))

    mag_wvlt = np.abs(cwt_haar(data, scale=scale))

    norm_mag_wvlt = np.abs(cwt_haar(data / np.abs(data), scale=scale))

    median_filter = cy_auto_interpretation.median_filter

    filtered_mag_wvlt = median_filter(mag_wvlt, k=median_filter_order)

    filtered_mag_norm_wvlt = median_filter(norm_mag_wvlt, k=median_filter_order)

    plt.subplot(421)
    plt.title("Original data")
    plt.plot(data)

    plt.subplot(422)
    plt.title("Amplitude normalized data")
    plt.plot(data / np.abs(data))

    plt.subplot(423)
    plt.title("CWT ({0:.4f})".format(np.var(mag_wvlt)))
    plt.plot(mag_wvlt)

    plt.subplot(424)
    plt.title("Filtered CWT ({0:.4f})".format(np.var(filtered_mag_wvlt)))
    plt.plot(filtered_mag_wvlt)

    plt.subplot(425)
    plt.title("Norm CWT ({0:.4f})".format(np.var(norm_mag_wvlt)))
    plt.plot(norm_mag_wvlt)

    plt.subplot(426)
    plt.title("Filtered Norm CWT ({0:.4f})".format(np.var(filtered_mag_norm_wvlt)))
    plt.plot(filtered_mag_norm_wvlt)

    plt.subplot(427)
    plt.title("FFT magnitude")
    fft = np.fft.fft(data)
    fft = np.abs(fft)
    ten_greatest_indices = np.argsort(fft)[::-1][0:10]
    print(ten_greatest_indices)
    print(fft[ten_greatest_indices])
    plt.plot(np.fft.fftshift(fft))

    plt.subplot(428)
    fft = np.fft.fftshift(np.fft.fft(data))
    fft[np.abs(fft) < 0.2 * np.max(np.abs(fft))] = 0
    fft_phase = np.angle(fft)
    ten_greatest_indices = np.argsort(np.abs(fft_phase))[::-1][0:10]
    print("FFT phases:")
    print(ten_greatest_indices)
    print(fft_phase[ten_greatest_indices])

    plt.title("FFT phase ({:.2f})".format(np.var(fft_phase)))
    plt.plot(fft_phase)

    plt.show()
