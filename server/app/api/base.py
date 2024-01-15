from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse

# Supporting versioned interfaces; a new (incompatible) API can be developed and grafted
# in here as desired. One approach might be to move the v1 API under a "/v1" tree and
# graft the new v2 API at the "root". Another continuous integration approach is to
# develop the new API under the "/v2" tree and not promote it to root until after beta
# testing with users
from .v1 import route_spectral

def include_router(router):
    '''This method connects all of the API pieces into the served web tree
    As new capabilities are added, a parent 'router' should be imported here
    and grafted in to the web tree at the desired point.

    This paradigm allows capabilities to remain ignorant of the path from which 
    they are served, and isolates the details of this app to this API tree.
    '''
    router.include_router(route_spectral.router, prefix="/spectral")

def make_router():
    '''This method encapsulates the creation and augmentation of the router for the API
    '''
    router = APIRouter()

    include_router(router)

    return router

# Define the global API router
router = make_router()

# Global API path definitions

@router.get("/")
async def get_root(request: Request):
    return RedirectResponse(url='index.html')

@router.get("/index.html")
async def get_root(request: Request):
    return FileResponse('static/index.html')


@router.get("/favicon.ico")
async def get_root(request: Request):
    return FileResponse('images/favicon.ico')
