import os
from redis_om import get_redis_connection
from config import settings

# Izvlačimo podatke koristeći os.getenv
redis = get_redis_connection(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True
)