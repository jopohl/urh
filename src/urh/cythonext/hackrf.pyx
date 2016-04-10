cimport chackrf
from libc.stdlib cimport malloc, free

cdef int _c_callback(chackrf.hackrf_transfer* transfer):
    print(transfer.buffer_length)


cdef class HackRF:
    cdef chackrf.hackrf_device* _c_device
    cdef int hackrf_success

    def __cinit__(self):
        self.hackrf_success = 0 #chackrf.hackrf_error.HACKRF_SUCCESS

    def setup(self):
        chackrf.hackrf_init()
        return self.__open()

    def exit(self):
        ret = self.__close()
        chackrf.hackrf_exit()
        return ret

    def __open(self):
        ret = chackrf.hackrf_open(&self._c_device)
        if ret == self.hackrf_success:
            print('Successfully opened HackRF device')
            return self.hackrf_success
        else:
            print('No HackRF detected!')

    def __close(self):
        ret = chackrf.hackrf_close(self._c_device)
        if ret == self.hackrf_success:
            print('Successfully closed HackRF device')
            return self.hackrf_success
        else:
            print('Failed to close HackRF!')

    def start_rx_mode(self, callback):
        ret = chackrf.hackrf_start_rx(self._c_device, _c_callback, <void *>0)
        if ret == self.hackrf_success:
            print('Successfully start HackRf in receive mode')
            return self.hackrf_success
        else:
            print('Failed to start HackRf in receive mode')

    def stop_rx_mode(self):
        ret = chackrf.hackrf_stop_rx(self._c_device)
        if ret == self.hackrf_success:
            print('Successfully stopped HackRF receive mode')
            return self.hackrf_success
        else:
            print('Failed to stop HackRF receive mode')
        return ret

    def start_tx_mode(self, callback):
        ret = chackrf.hackrf_start_tx(self._c_device, _c_callback, <void *>callback)
        if ret == self.hackrf_success:
            print('Successfully started HackRF in Transfer Mode')
            return self.hackrf_success
        else:
            print('Failed to start HackRF in Transfer Mode')

    def stop_tx_mode(self):
        ret = chackrf.hackrf_stop_tx(self._c_device)
        if ret == self.hackrf_success:
            print('Successfully stoped HackRF in Transfer Mode')
            return self.hackrf_success
        else:
            print('Failed to stop HackRF in Transfer Mode')

    def board_id_read(self):
        cdef unsigned char value
        ret = chackrf.hackrf_board_id_read(self._c_device, &value)
        if ret == self.hackrf_success:
            print('Successfully got Board Id')
            return value
        else:
            print('Failed to get Board Id')

    def version_string_read(self):
        cdef char* version = <char *>malloc(20 * sizeof(char))
        cdef unsigned char length = 20
        ret = chackrf.hackrf_version_string_read(self._c_device, version, length)
        if ret == self.hackrf_success:
            print('Successfully got HackRf Version String')
            return version.decode('UTF-8')
        else:
            print('Failed to get Version String')

    def set_freq(self, freq_hz):
        ret = chackrf.hackrf_set_freq(self._c_device, freq_hz)
        if ret == self.hackrf_success:
            print('Successfully set frequency with value', freq_hz)
            return self.hackrf_success
        else:
            print('Error setting frequency with value', freq_hz)

    def is_streaming(self):
        ret = chackrf.hackrf_is_streaming(self._c_device)
        if(ret == 1):
            return True
        else:
            return False

    def set_lna_gain(self, value):
        ''' Sets the LNA gain, in 8Db steps, maximum value of 40 '''
        result = chackrf.hackrf_set_lna_gain(self._c_device, value)
        if result == self.hackrf_success:
            print('Successfully set LNA gain to', value)
            return self.hackrf_success
        else:
            print('Failed to set LNA gain to', value)

    def set_vga_gain(self, value):
        ''' Sets the vga gain, in 2db steps, maximum value of 62 '''
        result = chackrf.hackrf_set_vga_gain(self._c_device, value)
        if result == self.hackrf_success:
            print('Successfully set VGA gain to', value)
            return self.hackrf_success
        else:
            print('Failed to set VGA gain to', value)

    def set_txvga_gain(self, value):
        ''' Sets the txvga gain, in 1db steps, maximum value of 47 '''
        result = chackrf.hackrf_set_txvga_gain(self._c_device, value)
        if result == self.hackrf_success:
            print('Successfully set TXVGA gain to', value)
            return self.hackrf_success
        else:
            print('Failed to set TXVGA gain to', value)


    def set_antenna_enable(self, value):
        cdef bint val = 1 if value else 0
        result =  chackrf.hackrf_set_antenna_enable(self._c_device, val)
        if result == self.hackrf_success:
            print('Successfully set antenna_enable')
            return self.hackrf_success
        else:
            print('Failed to set antenna_enable')

    def set_sample_rate(self, sample_rate):
        result = chackrf.hackrf_set_sample_rate(self._c_device, sample_rate)
        if result != self.hackrf_success:
            print('Error setting Sample Rate', sample_rate)
        else:
            print('Successfully set Sample Rate', sample_rate)
            return self.hackrf_success

    def set_amp_enable(self, value):
        cdef bint val = 1 if value else 0
        result =  chackrf.hackrf_set_amp_enable(self._c_device, val)
        if result == self.hackrf_success:
            print('Successfully set amp')
            return self.hackrf_success
        else:
            print('Failed to set amp')

    def set_baseband_filter_bandwidth(self, bandwidth_hz):
        result = chackrf.hackrf_set_baseband_filter_bandwidth(self._c_device, bandwidth_hz)
        if result != self.hackrf_success:
            print('Failed to set Baseband Filter Bandwidth with value', bandwidth_hz)
        else:
            print('Successfully set Baseband Filter Bandwidth with value', bandwidth_hz)
            return self.hackrf_success