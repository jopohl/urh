cimport chackrf
from libc.stdlib cimport malloc
from libc.string cimport memcpy
import time

from urh.util.Logger import logger

TIMEOUT = 0.2

cdef object f
from cpython cimport PyBytes_GET_SIZE

cdef int _c_callback_recv(chackrf.hackrf_transfer*transfer)  with gil:
    global f
    try:
        (<object> f)(transfer.buffer[0:transfer.valid_length])
        return 0
    except Exception as e:
        logger.error("Cython-HackRF:" + str(e))
        return -1

cdef int _c_callback_send(chackrf.hackrf_transfer*transfer)  with gil:
    global f
    # tostring() is a compatibility (numpy<1.9) alias for tobytes(). Despite its name it returns bytes not strings.
    cdef bytes bytebuf = (<object> f)(transfer.valid_length).tostring()
    memcpy(transfer.buffer, <void*> bytebuf, PyBytes_GET_SIZE(bytebuf))
    return 0

cdef chackrf.hackrf_device*_c_device
cdef int hackrf_success = chackrf.HACKRF_SUCCESS

cpdef setup():
    """
    Convenience method for init + open. This one is used by HackRF class.
    :return: 
    """
    init()
    return open()

cpdef init():
    return chackrf.hackrf_init()

cpdef open():
    return chackrf.hackrf_open(&_c_device)

cpdef exit():
    return chackrf.hackrf_exit()

cpdef reopen():
    close()
    return open()

cpdef close():
    return chackrf.hackrf_close(_c_device)

cpdef start_rx_mode(callback):
    global f
    f = callback
    return chackrf.hackrf_start_rx(_c_device, _c_callback_recv, <void*> _c_callback_recv)

cpdef stop_rx_mode():
    time.sleep(TIMEOUT)
    return chackrf.hackrf_stop_rx(_c_device)

cpdef start_tx_mode(callback):
    global f
    f = callback
    return chackrf.hackrf_start_tx(_c_device, _c_callback_send, <void *> _c_callback_send)

cpdef stop_tx_mode():
    time.sleep(TIMEOUT)
    return chackrf.hackrf_stop_tx(_c_device)

cpdef board_id_read():
    cdef unsigned char value
    ret = chackrf.hackrf_board_id_read(_c_device, &value)
    if ret == hackrf_success:
        return value
    else:
        return ""

cpdef version_string_read():
    cdef char*version = <char *> malloc(20 * sizeof(char))
    cdef unsigned char length = 20
    ret = chackrf.hackrf_version_string_read(_c_device, version, length)
    if ret == hackrf_success:
        return version.decode('UTF-8')
    else:
        return ""

cpdef set_freq(freq_hz):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_freq(_c_device, freq_hz)

cpdef is_streaming():
    time.sleep(TIMEOUT)
    ret = chackrf.hackrf_is_streaming(_c_device)
    if ret == 1:
        return True
    else:
        return False

cpdef set_rf_gain(value):
    """ Enable or disable RF amplifier """
    time.sleep(TIMEOUT)
    return set_amp_enable(value)

cpdef set_if_rx_gain(value):
    """ Sets the LNA gain, in 8Db steps, maximum value of 40 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_lna_gain(_c_device, value)

cpdef set_if_tx_gain(value):
    """ Sets the txvga gain, in 1db steps, maximum value of 47 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_txvga_gain(_c_device, value)

cpdef set_baseband_gain(value):
    """ Sets the vga gain, in 2db steps, maximum value of 62 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_vga_gain(_c_device, value)

cpdef set_sample_rate(sample_rate):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_sample_rate(_c_device, sample_rate)

cpdef set_amp_enable(value):
    time.sleep(TIMEOUT)
    cdef bint val = 1 if value else 0
    return chackrf.hackrf_set_amp_enable(_c_device, val)

cpdef set_baseband_filter_bandwidth(bandwidth_hz):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_baseband_filter_bandwidth(_c_device, bandwidth_hz)
