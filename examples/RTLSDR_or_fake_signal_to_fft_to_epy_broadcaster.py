#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Signal Content Portion of Web Based Spectrum Display
# Author: muaddib
# GNU Radio version: 3.10.7.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.fft import logpwrfft
from xmlrpc.server import SimpleXMLRPCServer
import threading
import RTLSDR_or_fake_signal_to_fft_to_epy_broadcaster_epy_broadcaster_block as epy_broadcaster_block  # embedded python block




class RTLSDR_or_fake_signal_to_fft_to_epy_broadcaster(gr.top_block):

    def __init__(self, fft_size=8192, frequency=100e6, gain=40.0, samp_rate=2.88e6):
        gr.top_block.__init__(self, "Signal Content Portion of Web Based Spectrum Display", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.fft_size = fft_size
        self.frequency = frequency
        self.gain = gain
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################

        self.xmlrpc_server_0 = SimpleXMLRPCServer(('localhost', 8001), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                300e3,
                60e3,
                window.WIN_HAMMING,
                6.76))
        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
            sample_rate=samp_rate,
            fft_size=fft_size,
            ref_scale=1,
            frame_rate=10,
            avg_alpha=1.0,
            average=False,
            shift=True)
        self.epy_broadcaster_block = epy_broadcaster_block.broadcaster(samp_rate=samp_rate, freq=frequency, gain=gain, fft_size=fft_size, redis_host="localhost", redis_port=6379, redis_stream="spectral")
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 500e3, .007, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, (-922e3), 0.0075, 0, 0)
        self.analog_noise_source_x_0_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 0.001, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, .038, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.analog_noise_source_x_0_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_add_xx_0, 0), (self.throttle, 0))
        self.connect((self.logpwrfft_x_0, 0), (self.epy_broadcaster_block, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.throttle, 0), (self.logpwrfft_x_0, 0))


    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.epy_broadcaster_block.freq = self.frequency

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.logpwrfft_x_0.set_sample_rate(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 300e3, 60e3, window.WIN_HAMMING, 6.76))
        self.throttle.set_sample_rate(self.samp_rate)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-n", "--fft-size", dest="fft_size", type=intx, default=8192,
        help="Set fft size [default=%(default)r]")
    parser.add_argument(
        "-f", "--frequency", dest="frequency", type=eng_float, default=eng_notation.num_to_str(float(100e6)),
        help="Set frequency [default=%(default)r]")
    parser.add_argument(
        "-g", "--gain", dest="gain", type=eng_float, default=eng_notation.num_to_str(float(40.0)),
        help="Set gain [default=%(default)r]")
    parser.add_argument(
        "-s", "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float(2.88e6)),
        help="Set sample rate [default=%(default)r]")
    return parser


def main(top_block_cls=RTLSDR_or_fake_signal_to_fft_to_epy_broadcaster, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(fft_size=options.fft_size, frequency=options.frequency, gain=options.gain, samp_rate=options.samp_rate)

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
