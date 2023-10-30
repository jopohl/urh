import time

from urh.signalprocessing.Modulator import Modulator


def test_fsk_performance():
    bit_data = "10" * 100 + "0000011111" + "001101011" * 100 + "111111100000" * 100
    modulator = Modulator("Perf")
    modulator.modulation_type = "FSK"
    t = time.time()
    result = modulator.modulate(bit_data, pause=10000000)
    elapsed = time.time() - t

    result.tofile("/tmp/fsk.complex")
    print("FSK {}ms".format(elapsed * 1000))


def test_ask_performance():
    bit_data = "10" * 100 + "0000011111" + "001101011" * 100 + "111111100000" * 1000
    modulator = Modulator("Perf")
    modulator.modulation_type = "ASK"
    t = time.time()
    result = modulator.modulate(bit_data, pause=10000000)
    elapsed = time.time() - t

    result.tofile("/tmp/ask.complex")
    print("ASK {}ms".format(elapsed * 1000))


def test_psk_performance():
    bit_data = "10" * 100 + "0000011111" + "001101011" * 100 + "111111100000" * 1000
    modulator = Modulator("Perf")
    modulator.modulation_type = "PSK"
    t = time.time()
    result = modulator.modulate(bit_data, pause=10000000)
    elapsed = time.time() - t

    result.tofile("/tmp/psk.complex")
    print("PSK {}ms".format(elapsed * 1000))


def test_gfsk_performance():
    bit_data = "10" * 100 + "0000011111" + "001101011" * 100 + "111111100000" * 100
    modulator = Modulator("Perf")
    modulator.modulation_type = "GFSK"
    t = time.time()
    result = modulator.modulate(bit_data, pause=10000000)
    elapsed = time.time() - t

    result.tofile("/tmp/gfsk.complex")
    print("GFSK {}ms".format(elapsed * 1000))


if __name__ == "__main__":
    test_fsk_performance()
