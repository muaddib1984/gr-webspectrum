from ..core.config import settings
from ..db.session import create_connection


async def get_stream_generator():
    '''
    Returns a spectral data generator suitable for passing to EventSourceResponse
    The generator should be called as 'generator(request:Request)'
    '''

    async def event_generator(request):
        last_id = '$'                     #most recent; prevents playing back old messages
        redisConn = await create_connection()
        sleep_ms = 100

        while True:
            # if client closes connection, stop sending events
            if await request.is_disconnected():
                break

            try:
                # Implementation note: if you support multiple streams, then this method
                # needs enough information to select the proper stream.
                stream_key = settings.SPECTRAL_STREAM_KEY
                resp = await redisConn.xread( {stream_key : last_id },
                                                  count=1,
                                                  block=sleep_ms)

                if resp:
                    key, messages = resp[0]
                    last_id, payload = messages[0]
                    decoded = payload['samples']
                    yield dict(data=decoded)
                else:
                    # No data was retrieved in the requested time; try again
                    pass

            except ConnectionError as e:
                print(f"ERROR: REDIS CONNECTION: {e}")

        await redisConn.close()
    # End of generator definition

    return event_generator
