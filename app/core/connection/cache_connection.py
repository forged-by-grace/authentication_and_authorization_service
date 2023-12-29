from core.utils.settings import settings
from  redis import asyncio as aioredis


redis = aioredis.from_url(
    url=settings.api_redis_host_local,    
)