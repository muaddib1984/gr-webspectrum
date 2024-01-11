from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from ...spectral import main as spectral

router = APIRouter()


@router.get('/')
async def get_root():
    return FileResponse('static/spectrum.html')

@router.get('/stream')
async def get_stream(request: Request,
                         ):
    '''This method serves the Server Side Events (SSE) to the browser
    The work is done in the generator, which is encapsulated independently
    from this API; the responsibility of the API is to interface with the browser.
    '''
    generator = await spectral.get_stream_generator()
    return EventSourceResponse(generator(request,))
