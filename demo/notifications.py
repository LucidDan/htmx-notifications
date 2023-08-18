"""
A small module handling notifications via redis pubsub.
"""
import json
from datetime import datetime
from functools import cache
import redis
import redis.asyncio as aredis
from django.conf import settings
from django.utils.timezone import now


@cache
def get_async_client() -> aredis.Redis:
    return aredis.from_url(settings.REDIS_URL)


@cache
def get_client() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL)


def send_notification(event: str, subject: str, message: str, ts: datetime, template: str = "demo/toast.html",):
    get_client().publish(
        event,
        json.dumps({
            "template": template,
            "context": {
                "subject": subject,
                "message": message,
                "message_time": ts.timestamp(),
            },
        })
    )
