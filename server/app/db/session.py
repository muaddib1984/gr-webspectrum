import redis.asyncio as redis

from ..core.config import settings


async def create_connection():
    conn = redis.Redis(host=settings.REDIS_HOSTNAME,
                           port=settings.REDIS_PORT,
                           retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                           decode_responses=settings.REDIS_DECODE_RESPONSES)
    return conn
