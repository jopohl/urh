from optparse import OptionParser
from InputHandlerThread import InputHandlerThread
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


if __name__ == '__main__':
    parser = OptionParser(usage='%prog: [options]')
    parser.add_option('-s', '--sample-rate', dest='sample_rate', default=100000)
    parser.add_option('-f', '--frequency', dest='frequency', default=433000)
    parser.add_option('-g', '--gain', dest='rf_gain', default=30)
    parser.add_option('-i', '--if-gain', dest='if_gain', default=30)
    parser.add_option('-b', '--bb-gain', dest='bb_gain', default=30)
    parser.add_option('-w', '--bandwidth', dest='bandwidth', default=250000)
    parser.add_option('-c', '--freq-correction', dest='freq_correction', default=0)
    parser.add_option('-d', '--direct-sampling', dest='direct_sampling', default=0)
    parser.add_option('-n', '--channel-index', dest='channel_index', default=0)
    parser.add_option('-a', '--antenna-index', dest='antenna_index', default=0)
    parser.add_option('-p', '--port', dest='port', default=1234)

    (options, args) = parser.parse_args()
    tb = top_block(int(options.sample_rate), int(options.frequency), int(options.freq_correction), int(options.rf_gain), int(options.if_gain), int(options.bb_gain), int(options.bandwidth), int(options.port))
    iht = InputHandlerThread(tb)
    iht.start()
    tb.start()
    tb.wait()
