"""
URL configuration and views

The 'urlpatterns' list at the end of this module routes URLs to views. In most cases
the views are also in this module. If the project gets big enough, move them to a
separate views.py file.
"""
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

from django.http import HttpRequest, HttpResponseBase, StreamingHttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import path
from django.utils.timezone import now

from demo.notifications import get_async_client, send_notification


def index(request: HttpRequest) -> HttpResponseBase:
    return render(request, "demo/index.html", {})


async def streamed_events(event_name: str, request: HttpRequest) -> AsyncGenerator[str, None]:
    """Listen for events and generate an SSE message for each event"""

    try:
        async with get_async_client().pubsub() as pubsub:
            await pubsub.subscribe(event_name)
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
                if msg is None:
                    continue
                data = json.loads(msg["data"])
                if data.get("template", "") == "STOP":
                    break
                template = data.pop("template")
                data["message_time"] = datetime.fromtimestamp(data["message_time"])
                # Strip out the newlines, to avoid issues
                text = render_to_string(template, data, request).replace("\n", "")
                yield f"data: {text}\n\n"
    except asyncio.CancelledError:
        # Do any cleanup when the client disconnects

        # Note: this will only be called starting from Django 5.0
        # until then, there is no cleanup, and you get some spammy
        # 'took too long to shut down and was killed' log messages from Daphne etc.
        raise


async def events(request: HttpRequest, event_name: str) -> HttpResponseBase:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", ])
    return StreamingHttpResponse(
        streaming_content=streamed_events(event_name, request),
        content_type="text/event-stream",
    )


def send_event(request: HttpRequest) -> HttpResponseBase:
    send_notification(
        event="toasts",
        subject="Trip Cancellation",
        message="The trip 'Kenya May 2024' has been cancelled.",
        ts=now(),
        template="demo/toast.html",
    )
    return render(request, "demo/send_event.html", {})


async def sse(request: HttpRequest) -> HttpResponseBase:
    async def stream(request: HttpRequest) -> AsyncGenerator[str, None]:
        counter = 0
        while True:
            counter += 1
            asyncio.sleep(5.0)
            yield f"data: {counter}\n\n"

    return StreamingHttpResponse(
        streaming_content=stream(request),
        content_type="text/event-stream",
    )


urlpatterns = [
    path("", index, name="home"),
    path("send/", send_event, name="send-event"),
    path("events/<str:event_name>/", events, name="events"),
    path("sse/", sse, name="basic-sse")
]
