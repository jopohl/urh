from optparse import OptionParser
import Initializer

Initializer.init_path()


import signal
import sys

import osmosdr
from gnuradio import blocks
from gnuradio import gr


class top_block(gr.top_block):

    def __init__(self, sample_rate, frequency, freq_correction, rf_gain, if_gain, bb_gain, bandwidth, port):
        gr.top_block.__init__(self, "Top Block")

        self.sample_rate = sample_rate 
        self.rf_gain = rf_gain 
        self.port = port 
        self.if_gain = if_gain 
        self.frequency = frequency 
        self.freq_correction = freq_correction 
        self.bb_gain = bb_gain 
        self.bandwidth = bandwidth 

        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'airspy'
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(sample_rate)
        self.osmosdr_source_0.set_center_freq(frequency, 0)
        self.osmosdr_source_0.set_freq_corr(freq_correction, 0)
        self.osmosdr_source_0.set_gain(rf_gain, 0)
        self.osmosdr_source_0.set_if_gain(if_gain, 0)
        self.osmosdr_source_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(bandwidth, 0)
        self.blocks_tcp_server_sink_0 = blocks.tcp_server_sink(gr.sizeof_gr_complex * 1, '127.0.0.1', port, False)

        self.connect((self.osmosdr_source_0, 0), (self.blocks_tcp_server_sink_0, 0))

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.osmosdr_source_0.set_sample_rate(self.sample_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.osmosdr_source_0.set_gain(self.rf_gain, 0)

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_source_0.set_if_gain(self.if_gain, 0)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.osmosdr_source_0.set_center_freq(self.frequency, 0)

    def get_freq_correction(self):
        return self.freq_correction

    def set_freq_correction(self, freq_correction):
        self.freq_correction = freq_correction
        self.osmosdr_source_0.set_freq_corr(self.freq_correction, 0)

    def get_direct_sampling_mode(self):
        return self.direct_sampling_mode

    def set_direct_sampling_mode(self, direct_sampling_mode):
        self.direct_sampling_mode = direct_sampling_mode

    def get_channel_index(self):
        return self.channel_index

    def set_channel_index(self, channel_index):
        self.channel_index = channel_index

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.osmosdr_source_0.set_bb_gain(self.bb_gain, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.osmosdr_source_0.set_bandwidth(self.bandwidth, 0)

    def get_antenna_index(self):
        return self.antenna_index

    def set_antenna_index(self, antenna_index):
        self.antenna_index = antenna_index


def main(top_block_cls=top_block, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
