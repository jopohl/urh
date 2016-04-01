#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Aug 16 17:45:11 2015
##################################################

from optparse import OptionParser

from gnuradio import blocks
from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2


class top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 10000000

        ##################################################
        # Blocks
        ##################################################
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex * 1,
                                                       "/home/joe/SVN/noack/USRP/Fabema/Testdata/trafficlight_fhside_full.complex",
                                                       False)
        self.blks2_tcp_sink_0 = grc_blks2.tcp_sink(
            itemsize=gr.sizeof_gr_complex * 1,
            addr="127.0.0.1",
            port=1337,
            server=True,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blks2_tcp_sink_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.start()
    tb.wait()
