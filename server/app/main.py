from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import api
from .core.config import settings


def include_router(app):
    'This method ties in sub-trees'
    app.include_router(api.base.router)


def configure_static(app):
    'This method creates mount points'
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.mount('/images', StaticFiles(directory='images'), name='images')


def start_application():
    'This method creates the app'
    app = FastAPI(title=settings.PROJECT_NAME,
                      version=settings.PROJECT_VERSION)

    include_router(app)
    configure_static(app)

    return app

# The global app started by uvicorn or ASGI server of your choice
app = start_application()
