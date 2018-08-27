import numpy as np

from urh.cythonext import auto_interpretation as  cy_auto_interpretation


def normalized_haar_wavelet(omega, scale):
    omega_cpy = omega[:] / scale
    omega_cpy[0] = 1.0  # first element always zero, so prevent division by zero later

    result = (1j * (-1 + np.exp(0.5j * omega)) ** 2) / omega_cpy
    return result


def cwt_haar(x: np.ndarray, scale=10):
    """
    continuous haar wavelet transform based on the paper
    "A practical guide to wavelet analysis" by Christopher Torrence and Gilbert P Compo

    """

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
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask_short.complex", dtype=np.complex64)

    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask50.complex", dtype=np.complex64)
    # Wavelet transform the data
    # data = np.fromfile("/home/joe/GIT/urh/tests/data/ask.complex", dtype=np.complex64)[0:2 ** 13]

    # data = np.fromfile("/tmp/generated.complex", dtype=np.complex64)

    data = np.fromfile("/tmp/psk.complex", dtype=np.complex64)

    # data = np.fromfile("/tmp/ask25.complex", dtype=np.complex64)
    # data = np.fromfile("/tmp/ask1080.complex", dtype=np.complex64)

    scale = 4
    median_filter_order = 11

    mag_wvlt = np.abs(cwt_haar(data, scale=scale))

    # Multiply with max of data to prevent increasing variance for signals with lower amplitude
    norm_mag_wvlt = np.abs(cwt_haar(np.max(data) * data / np.abs(data), scale=scale))

    median_filter = cy_auto_interpretation.median_filter

    filtered_mag_wvlt = median_filter(mag_wvlt, k=median_filter_order)

    filtered_mag_norm_wvlt = median_filter(norm_mag_wvlt, k=median_filter_order)

    plt.subplot(221)
    plt.title("CWT ({0:.4f})".format(np.var(mag_wvlt)))
    plt.plot(mag_wvlt)

    plt.subplot(222)
    plt.title("Filtered CWT ({0:.4f})".format(np.var(filtered_mag_wvlt)))
    plt.plot(filtered_mag_wvlt)

    plt.subplot(223)
    plt.title("Norm CWT ({0:.4f})".format(np.var(norm_mag_wvlt)))
    plt.plot(norm_mag_wvlt)

    plt.subplot(224)
    plt.title("Filtered Norm CWT ({0:.4f})".format(np.var(filtered_mag_norm_wvlt)))
    plt.plot(filtered_mag_norm_wvlt)

    plt.show()
