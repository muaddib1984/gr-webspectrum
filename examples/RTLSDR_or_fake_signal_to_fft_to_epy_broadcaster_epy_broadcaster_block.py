import numpy as np
from gnuradio import gr
from redis import Redis
import json
class broadcaster(gr.sync_block):
    """
    docstring for block broadcaster
    """
    def __init__(self, samp_rate=2.88e6,freq=100e6,gain=40.0,fft_size=8192,redis_host="localhost",redis_port=6379,redis_stream="spectral"):
        gr.sync_block.__init__(self,
            name="broadcaster",
            in_sig=[(np.float32, fft_size)],
            out_sig=None)
        self.redis_host=redis_host
        self.redis_port=redis_port
        self.redis_stream=redis_stream
        self.r=Redis(redis_host,redis_port, retry_on_timeout=True)
        self.freq=freq
    def work(self, input_items, output_items):

        # input_items is a vector of "samples". Each sample is a vector of length fft_size
        ninput_items = len(input_items[0])

        for msg in input_items[0]:
            p = np.around(msg).astype(int)
            # For reasonable performance, the Redis stream is a JSON-encoded list (a string). Otherwise,
            # serialization can be costly
            data = {"samples": json.dumps(p.tolist())}
            data["frequency"]=self.freq
            # maxlen=100 says to only keep the last 100 messages. This prevents old data from streaming
            self.r.xadd(self.redis_stream, data, maxlen=100)

        self.consume(0, ninput_items)

        return 0
