import numpy as np

from urh.cythonext.signal_functions import afp_demod


def normalized_haar_wavelet(s_times_omega):
    # https://gist.github.com/patoorio/a9f60ef16489639fbf20f23ac49ba24f
    result = np.zeros(len(s_times_omega), np.complex64)
    om = s_times_omega[:]
    om[0] = 1.0  # prevent divide error
    result.imag = 4.0 * np.sin(s_times_omega / 2) ** 2 / om
    return result


def continuous_haar_wavelet_transform(x: np.ndarray, scale=10):
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
    psi_hat = np.sqrt(2.0 * np.pi * scale) * normalized_haar_wavelet(scale * omega)

    # get W (eq. (4) in paper)
    W = np.fft.ifft(x_hat * psi_hat)

    return W


def median_filter(data: np.ndarray, k=3):
    n = len(data)

    result = np.zeros(n, dtype=data.dtype)

    for i in range(0, n):
        start = max(0, i - k // 2)
        end = min(n, i + k // 2 + 1)
        result[i] = np.median(data[start:end])

    return result


def get_variances(data: np.ndarray, scale=10, k=3):
    """
    get variances of wavelet transform data without and with amplitude normalization

    Ref: Identification of digital modulation types using the wavelet transform by Hong, Liang and Ho, K.C.

    :param k: Filter order for median filter
    :param scale: Scale for wavelet transform
    :param data:
    :return:
    """

    data = data[np.abs(data) != 0]

    mag_cwt = np.abs(continuous_haar_wavelet_transform(data, scale=scale))
    filtered_mag = median_filter(mag_cwt, k=k)

    normalized_mag_cwt = np.abs(continuous_haar_wavelet_transform(data / np.abs(data), scale=scale))
    normalized_mag_filtered = median_filter(normalized_mag_cwt, k=k)

    return np.var(filtered_mag), np.var(normalized_mag_filtered)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    #data = np.fromfile("/home/joe/GIT/urh/tests/data/fsk.complex", dtype=np.complex64)[:2 ** 11]

    # Wavelet transform the data
    #data = np.fromfile("/home/joe/GIT/urh/tests/data/ask.complex", dtype=np.complex64)[0:2 ** 13]

    #data = np.fromfile("/tmp/generated.complex", dtype=np.complex64)

    data = np.fromfile("/tmp/psk.complex", dtype=np.complex64)

    data = data[np.abs(data) != 0]
    data = data / np.abs(data)

    demod = afp_demod(data, 0, 1) * np.abs(data)

    wvlt = continuous_haar_wavelet_transform(data, scale=7)
    mag_wvlt = np.abs(wvlt)
    print("Variance", np.var(mag_wvlt))

    print(mag_wvlt[90:120])
    filtered_mag_wvlt = median_filter(mag_wvlt, k=3)
    print("Filtered Variance", np.var(filtered_mag_wvlt))

    plt.subplot(211)
    plt.plot(mag_wvlt)
    plt.subplot(212)
    plt.plot(filtered_mag_wvlt)

    plt.show()
