#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Fri Aug 21 15:56:13 2015
##################################################

from optparse import OptionParser

import tempfile
import os
import sys
try:
    with open(os.path.join(tempfile.gettempdir(), "gnuradio_path.txt"), "r") as f:
        gnuradio_path = f.read().strip()

    os.environ["PATH"] = os.path.join(gnuradio_path, "bin")
    sys.path.insert(0, os.path.join(gnuradio_path, "lib", "site-packages"))

except IOError:
    pass

from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2
from InputHandlerThread import InputHandlerThread
import osmosdr
from gnuradio import zeromq

class top_block(gr.top_block):
    def __init__(self, samp_rate, freq, gain, bw, port):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate
        self.gain = gain
        self.freq = freq
        self.bw = bw

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source(args="numchan=" + str(1) + " " + "sdrplay")
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(gain, 0)
        self.osmosdr_source_0.set_if_gain(gain, 0)
        self.osmosdr_source_0.set_bb_gain(gain, 0)
        self.osmosdr_source_0.set_antenna("", 0)
        self.osmosdr_source_0.set_bandwidth(bw, 0)

        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:' + str(port))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.zeromq_push_sink_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.osmosdr_source_0.set_gain(self.gain, 0)
        self.osmosdr_source_0.set_if_gain(self.gain, 0)
        self.osmosdr_source_0.set_bb_gain(self.gain, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.osmosdr_source_0.set_bandwidth(self.bw, 0)


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-s", "--samplerate", dest="samplerate", help="Sample Rate", default=100000)
    parser.add_option("-f", "--freq", dest="freq", help="Frequency", default=433000)
    parser.add_option("-g", "--gain", dest="gain", help="Gain", default=30)
    parser.add_option("-b", "--bandwidth", dest="bw", help="Bandwidth", default=200000)
    parser.add_option("-p", "--port", dest="port", help="Port", default=1337)
    (options, args) = parser.parse_args()
    tb = top_block(float(options.samplerate), float(options.freq), int(options.gain),
                   float(options.bw), int(options.port))
    iht = InputHandlerThread(tb)
    iht.start()
    tb.start()
    tb.wait()
