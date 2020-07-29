cimport urh.dev.native.lib.chackrf as chackrf
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from libc.stdlib cimport malloc
import time

from urh.util.Logger import logger

TIMEOUT = 0.2

cdef object f
cdef int RUNNING = 0

cdef int _c_callback_recv(chackrf.hackrf_transfer*transfer)  with gil:
    global f, RUNNING
    try:
        (<object> f)(transfer.buffer[0:transfer.valid_length])
        return RUNNING
    except Exception as e:
        logger.error("Cython-HackRF:" + str(e))
        return -1

cdef int _c_callback_send(chackrf.hackrf_transfer*transfer)  with gil:
    global f, RUNNING
    # tostring() is a compatibility (numpy<1.9) alias for tobytes(). Despite its name it returns bytes not strings.
    cdef unsigned int i
    cdef unsigned int valid_length = <unsigned int>transfer.valid_length
    cdef unsigned char[:] data  = (<object> f)(valid_length)
    cdef unsigned int loop_end = min(len(data), valid_length)

    for i in range(0, loop_end):
        transfer.buffer[i] = data[i]

    for i in range(loop_end, valid_length):
        transfer.buffer[i] = 0

    # Need to return -1 on finish, otherwise stop_tx_mode hangs forever
    # Furthermore, this leads to windows issue https://github.com/jopohl/urh/issues/360
    return RUNNING

cdef chackrf.hackrf_device*_c_device
cdef int hackrf_success = chackrf.HACKRF_SUCCESS

IF HACKRF_MULTI_DEVICE_SUPPORT == 1:
    cpdef has_multi_device_support():
        return True
    cpdef open(str serial_number=""):
        if not serial_number:
            return chackrf.hackrf_open(&_c_device)

        desired_serial = serial_number.encode('UTF-8')
        c_desired_serial = <char *> desired_serial
        return chackrf.hackrf_open_by_serial(c_desired_serial, &_c_device)
    cpdef get_device_list():
        init()
        cdef chackrf.hackrf_device_list_t* device_list = chackrf.hackrf_device_list()

        result = []
        cdef int i
        for i in range(device_list.devicecount):
            serial_number = device_list.serial_numbers[i].decode("UTF-8")
            result.append(serial_number)

        chackrf.hackrf_device_list_free(device_list)
        exit()
        return result
ELSE:
    cpdef has_multi_device_support():
        return False
    cpdef open(str serial_number=""):
        return chackrf.hackrf_open(&_c_device)
    cpdef get_device_list():
        return None

cpdef int setup(str serial):
    """
    Convenience method for init + open. This one is used by HackRF class.
    :return: 
    """
    init()
    return open(serial)

cpdef int init():
    return chackrf.hackrf_init()

cpdef int exit():
    return chackrf.hackrf_exit()

cpdef int close():
    return chackrf.hackrf_close(_c_device)

cpdef int start_rx_mode(callback):
    global f, RUNNING
    RUNNING = 0
    f = callback
    return chackrf.hackrf_start_rx(_c_device, _c_callback_recv, NULL)

cpdef int stop_rx_mode():
    global RUNNING
    RUNNING = -1
    time.sleep(TIMEOUT)
    return chackrf.hackrf_stop_rx(_c_device)

cpdef int start_tx_mode(callback):
    global f, RUNNING
    RUNNING = 0
    f = callback
    return chackrf.hackrf_start_tx(_c_device, _c_callback_send, NULL)

cpdef int stop_tx_mode():
    global RUNNING
    RUNNING = -1
    time.sleep(TIMEOUT)
    return chackrf.hackrf_stop_tx(_c_device)

cpdef int set_freq(freq_hz):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_freq(_c_device, freq_hz)

cpdef is_streaming():
    time.sleep(TIMEOUT)
    ret = chackrf.hackrf_is_streaming(_c_device)
    if ret == 1:
        return True
    else:
        return False

cpdef int set_amp_enable(value):
    time.sleep(TIMEOUT)
    cdef uint8_t val = 1 if value else 0
    return chackrf.hackrf_set_amp_enable(_c_device, val)

cpdef int set_rf_gain(value):
    """ Enable or disable RF amplifier """
    return set_amp_enable(value)

cpdef int set_if_rx_gain(value):
    """ Sets the LNA gain, in 8Db steps, maximum value of 40 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_lna_gain(_c_device, value)

cpdef int set_if_tx_gain(value):
    """ Sets the txvga gain, in 1db steps, maximum value of 47 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_txvga_gain(_c_device, value)

cpdef int set_baseband_gain(value):
    """ Sets the vga gain, in 2db steps, maximum value of 62 """
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_vga_gain(_c_device, value)

cpdef int set_sample_rate(sample_rate):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_sample_rate(_c_device, sample_rate)

cpdef int set_bias_tee(on_or_off):
    time.sleep(TIMEOUT)
    cdef uint8_t bias_tee = 1 if on_or_off else 0
    return chackrf.hackrf_set_antenna_enable(_c_device, bias_tee)

cpdef int set_baseband_filter_bandwidth(bandwidth_hz):
    time.sleep(TIMEOUT)
    return chackrf.hackrf_set_baseband_filter_bandwidth(_c_device, bandwidth_hz)
