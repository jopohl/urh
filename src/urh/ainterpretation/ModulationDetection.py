import numpy as np


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



if __name__ == "__main__":
    from matplotlib import pyplot as plt

    data = np.fromfile("/tmp/test.complex", dtype=np.complex64)[:2**15]
    # Wavelet transform the data
    #data = np.fromfile("/home/joe/GIT/urh/tests/data/ask.complex", dtype=np.complex64)[0:2 ** 13]

    #data = data / np.abs(data)

    wvlt = continuous_haar_wavelet_transform(data, scale=10)

    print(np.var(np.abs(wvlt)))

    plt.plot(np.abs(wvlt))

    plt.show()