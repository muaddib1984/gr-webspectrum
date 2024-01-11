from starlette.config import Config

# Any settings here can be overriden by a ".env" file in the directory from which the
# server is started
config = Config('.env')

class Settings:
    PROJECT_NAME: str = 'gr-webspectrum'
    PROJECT_VERSION: str = '0.1.0'

    REDIS_HOSTNAME: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DECODE_RESPONSES: bool = True

    SPECTRAL_STREAM_KEY: str = 'spectral'
    FREQ_STREAM_KEY: str = 'frequency'

settings = Settings()
