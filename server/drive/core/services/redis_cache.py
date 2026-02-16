import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS["HOST"],
    port=settings.REDIS["PORT"],
    db=settings.REDIS["DB"],
    password=settings.REDIS["PASSWORD"],
    socket_timeout=settings.REDIS["SOCKET_TIMEOUT"],
    decode_responses=settings.REDIS["DECODE_RESPONSES"],
)

TASK_OWNER_KEY = "downloading:celery:task_owner"
VECTOR_OWNER_KEY = "vectorise:celery:task_owner"
VECTOR_STATUS_KEY = "vectorise:celery:task_status"