cimport chackrf
cimport numpy as np
from libc.stdio cimport * # printf fflush
from libc.stdlib cimport malloc, free
cdef object f
#cdef unsigned char[:] buffer = np.empty(10000000000000)

cdef int _c_callback(chackrf.hackrf_transfer* transfer) nogil:
    global f
    printf("%d %d\n", transfer.buffer_length, transfer.valid_length)
    printf("%d\n", transfer.buffer[0])

    return 0

cdef chackrf.hackrf_device* _c_device
cdef int hackrf_success = chackrf.HACKRF_SUCCESS


cpdef setup():
    chackrf.hackrf_init()
    return open()

cpdef exit():
    ret = close()
    chackrf.hackrf_exit()
    return ret

cpdef open():
    ret = chackrf.hackrf_open(&_c_device)
    if ret == hackrf_success:
        print('Successfully opened HackRF device')
        return hackrf_success
    else:
        print('No HackRF detected!')

cpdef close():
    ret = chackrf.hackrf_close(_c_device)
    if ret == hackrf_success:
        print('Successfully closed HackRF device')
        return hackrf_success
    else:
        print('Failed to close HackRF!')

cpdef start_rx_mode(callback):
    global f
    f  = callback
    ret = chackrf.hackrf_start_rx(_c_device, _c_callback, <void*>_c_callback)
    if ret == hackrf_success:
        print('Successfully start HackRf in receive mode')
        return hackrf_success
    else:
        print('Failed to start HackRf in receive mode')

cpdef stop_rx_mode():
    ret = chackrf.hackrf_stop_rx(_c_device)
    if ret == hackrf_success:
        print('Successfully stopped HackRF receive mode')
        return hackrf_success
    else:
        print('Failed to stop HackRF receive mode')
    return ret

cpdef start_tx_mode( callback):
    global f
    f = callback
    ret = chackrf.hackrf_start_tx(_c_device, _c_callback, <void *>callback)
    if ret == hackrf_success:
        print('Successfully started HackRF in Transfer Mode')
        return hackrf_success
    else:
        print('Failed to start HackRF in Transfer Mode')

cpdef stop_tx_mode():
    ret = chackrf.hackrf_stop_tx(_c_device)
    if ret == hackrf_success:
        print('Successfully stoped HackRF in Transfer Mode')
        return hackrf_success
    else:
        print('Failed to stop HackRF in Transfer Mode')

cpdef board_id_read():
    cdef unsigned char value
    ret = chackrf.hackrf_board_id_read(_c_device, &value)
    if ret == hackrf_success:
        print('Successfully got Board Id')
        return value
    else:
        print('Failed to get Board Id')

cpdef version_string_read():
    cdef char* version = <char *>malloc(20 * sizeof(char))
    cdef unsigned char length = 20
    ret = chackrf.hackrf_version_string_read(_c_device, version, length)
    if ret == hackrf_success:
        print('Successfully got HackRf Version String')
        return version.decode('UTF-8')
    else:
        print('Failed to get Version String')

cpdef set_freq(freq_hz):
    ret = chackrf.hackrf_set_freq(_c_device, freq_hz)
    if ret == hackrf_success:
        print('Successfully set frequency with value', freq_hz)
        return hackrf_success
    else:
        print('Error setting frequency with value', freq_hz)

cpdef is_streaming():
    ret = chackrf.hackrf_is_streaming(_c_device)
    if(ret == 1):
        return True
    else:
        return False

cpdef set_lna_gain( value):
    ''' Sets the LNA gain, in 8Db steps, maximum value of 40 '''
    result = chackrf.hackrf_set_lna_gain(_c_device, value)
    if result == hackrf_success:
        print('Successfully set LNA gain to', value)
        return hackrf_success
    else:
        print('Failed to set LNA gain to', value)

cpdef set_vga_gain( value):
    ''' Sets the vga gain, in 2db steps, maximum value of 62 '''
    result = chackrf.hackrf_set_vga_gain(_c_device, value)
    if result == hackrf_success:
        print('Successfully set VGA gain to', value)
        return hackrf_success
    else:
        print('Failed to set VGA gain to', value)

cpdef set_txvga_gain( value):
    ''' Sets the txvga gain, in 1db steps, maximum value of 47 '''
    result = chackrf.hackrf_set_txvga_gain(_c_device, value)
    if result == hackrf_success:
        print('Successfully set TXVGA gain to', value)
        return hackrf_success
    else:
        print('Failed to set TXVGA gain to', value)


cpdef set_antenna_enable( value):
    cdef bint val = 1 if value else 0
    result =  chackrf.hackrf_set_antenna_enable(_c_device, val)
    if result == hackrf_success:
        print('Successfully set antenna_enable')
        return hackrf_success
    else:
        print('Failed to set antenna_enable')

cpdef set_sample_rate( sample_rate):
    result = chackrf.hackrf_set_sample_rate(_c_device, sample_rate)
    if result != hackrf_success:
        print('Error setting Sample Rate', sample_rate)
    else:
        print('Successfully set Sample Rate', sample_rate)
        return hackrf_success

cpdef set_amp_enable( value):
    cdef bint val = 1 if value else 0
    result =  chackrf.hackrf_set_amp_enable(_c_device, val)
    if result == hackrf_success:
        print('Successfully set amp')
        return hackrf_success
    else:
        print('Failed to set amp')

cpdef set_baseband_filter_bandwidth(bandwidth_hz):
    result = chackrf.hackrf_set_baseband_filter_bandwidth(_c_device, bandwidth_hz)
    if result != hackrf_success:
        print('Failed to set Baseband Filter Bandwidth with value', bandwidth_hz)
    else:
        print('Successfully set Baseband Filter Bandwidth with value', bandwidth_hz)
        return hackrf_success