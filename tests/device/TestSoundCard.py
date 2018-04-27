def test_sounddevice_lib():
    import time

    import numpy as np
    import sounddevice as sd
    """ 
    if no portaudio installed:
    Traceback (most recent call last):
  File "TestSoundCard.py", line 42, in <module>
    test_sounddevice_lib()
  File "TestSoundCard.py", line 5, in test_sounddevice_lib
    import sounddevice as sd
  File "/usr/lib/python3.6/site-packages/sounddevice.py", line 64, in <module>
    raise OSError('PortAudio library not found')
  OSError: PortAudio library not found

    """


    duration = 2.5  # seconds

    rx_buffer = np.ones((10 ** 6, 2), dtype=np.float32)
    global current_rx, current_tx
    current_rx = 0
    current_tx = 0

    def rx_callback(indata: np.ndarray, frames: int, time, status):
        global current_rx
        if status:
            print(status)

        rx_buffer[current_rx:current_rx + frames] = indata
        current_rx += frames

    def tx_callback(outdata: np.ndarray, frames: int, time, status):
        global current_tx
        if status:
            print(status)

        outdata[:] = rx_buffer[current_tx:current_tx + frames]
        current_tx += frames

    with sd.InputStream(channels=2, callback=rx_callback):
        time.sleep(duration)

    print("Current rx", current_rx)

    with sd.OutputStream(channels=2, callback=tx_callback):
        sd.sleep(int(duration * 1000))

    print("Current tx", current_tx)


if __name__ == '__main__':
    test_sounddevice_lib()
