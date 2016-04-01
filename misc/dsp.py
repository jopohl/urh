import numpy as np
import matplotlib.pyplot as plt

f_s = 600
t_s = 1 / f_s

f_c = 20
bit_len = 100
bits = [True, True, False, False, True]

# FSK
y = []
for i, b in enumerate(bits):
    factor = 1 if b else 0.5
    y.extend(np.cos(2 * np.pi * (f_c * factor) * t_s * np.arange(i * bit_len, (i + 1) * bit_len)))

x = np.arange(0, len(bits) * bit_len)
plt.subplot(311)
plt.plot(x, y)

plt.subplot(312)
# IQ Bilden
iq_signal = []
v = []
for n, value in enumerate(y):
    iq_signal.append(np.exp(-1j * 2 * np.pi * f_c * t_s * n) * value)
iq_signal = np.array(iq_signal)

plt.plot(x, iq_signal.real)

plt.subplot(313)

angles = [0]
for i in range(1, len(iq_signal)):
    prev_sample = iq_signal[i - 1]
    sample = iq_signal[i]
    angles.append(np.arctan2(prev_sample.imag, prev_sample.real) - np.arctan2(sample.imag, sample.real))

plt.plot(x, angles, "ro")
plt.show()
