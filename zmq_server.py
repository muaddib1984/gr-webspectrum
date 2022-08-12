#!/usr/bin/env python

# Copyright (c) 2019 Jeppe Ledet-Pedersen
# This software is released under the MIT license.
# See the LICENSE file for further details.

import sys
import json
import argparse

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq
import numpy as np

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

from bottle import request, Bottle, abort, static_file


app = Bottle()
connections = set()
opts = {}


@app.route('/websocket')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    connections.add(wsock)

    # Send center frequency and span
    wsock.send(json.dumps(opts))

    while True:
        try:
            wsock.receive()
        except WebSocketError:
            break

    connections.remove(wsock)


@app.route('/')
def index():
    return static_file('index.html', root='.')


@app.route('/<filename>')
def static(filename):
    return static_file(filename, root='.')


class fft_broadcast_sink(gr.sync_block):
    def __init__(self, fft_size):
        gr.sync_block.__init__(self,
                               name="plotter",
                               in_sig=[(np.float32, fft_size)],
                               out_sig=[])

    def work(self, input_items, output_items):
        ninput_items = len(input_items[0])
        for bins in input_items[0]:

            p = np.around(bins).astype(int)
#            p = np.fft.fftshift(p)
            for c in connections.copy():
                try:
                    c.send(json.dumps({'s': p.tolist()}, separators=(',', ':')))
                except Exception:
                    connections.remove(c)

        self.consume(0, ninput_items)

        return 0


class fft_receiver(gr.top_block):
    def __init__(self, samp_rate, freq, fft_size, framerate): #    def __init__(self, samp_rate, freq, gain, fft_size, framerate):
        gr.top_block.__init__(self, "Top Block")
        self.zmq_sub_source = zeromq.sub_source(
            gr.sizeof_float,
            fft_size,
            'tcp://localhost:5001',
            100,
            False,
            -1,
            '')

        self.throttle = blocks.throttle(
            gr.sizeof_float*fft_size,
            samp_rate,
            True)

        self.fft_broadcast = fft_broadcast_sink(fft_size)

        self.connect((self.throttle, 0), (self.fft_broadcast, 0))
        self.connect((self.zmq_sub_source, 0), (self.throttle, 0))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sample-rate', type=float, default=200e6)
    parser.add_argument('-f', '--frequency', type=float, default=1600e6)
#    parser.add_argument('-g', '--gain', type=float, default=40)
    parser.add_argument('-n', '--fft-size', type=int, default=4096)
    parser.add_argument('-r', '--frame-rate', type=int, default=25)

    args = parser.parse_args()


    tb = fft_receiver(
        samp_rate=args.sample_rate,
        freq=args.frequency,
#        gain=args.gain,
        fft_size=args.fft_size,
        framerate=args.frame_rate
    )
    tb.start()

    opts['center'] = args.frequency
    opts['span'] = args.sample_rate

    server = WSGIServer(("0.0.0.0", 8200), app,
                        handler_class=WebSocketHandler)
    try:
        server.serve_forever()
    except Exception:
        sys.exit(0)

    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
