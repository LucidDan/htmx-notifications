"""
URL configuration and views

The 'urlpatterns' list at the end of this module routes URLs to views. In most cases
the views are also in this module. If the project gets big enough, move them to a
separate views.py file.
"""
import asyncio
import json
import random
from datetime import datetime
from typing import AsyncGenerator

from django.http import HttpRequest, HttpResponseBase, StreamingHttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import path
from django.utils.timezone import now

from demo.notifications import get_async_client, send_notification


def index(request: HttpRequest) -> HttpResponseBase:
    """Display the main home page"""

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
                ctx = data["context"]
                template = data.get("template", "")
                if template == "STOP":
                    break
                elif not template:
                    continue
                ctx["message_time"] = datetime.fromtimestamp(ctx["message_time"])
                # Strip out the newlines, to avoid issues. Clunky, I know, fix this properly later.
                text = render_to_string(template, ctx, request).replace("\n", "")
                yield f"data: {text}\n\n"
    except asyncio.CancelledError:
        # Do any cleanup when the client disconnects
        # Note: this will only be called starting from Django 5.0; until then, there is no cleanup,
        # and you get some spammy 'took too long to shut down and was killed' log messages from Daphne etc.
        raise


def events(request: HttpRequest, event_name: str) -> HttpResponseBase:
    """Start an SSE connection for event_name"""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", ])
    return StreamingHttpResponse(
        streaming_content=streamed_events(event_name, request),
        content_type="text/event-stream",
    )


def send_event(request: HttpRequest) -> HttpResponseBase:
    """A little endpoint to send requests to which will trigger an event to be enqueued"""

    location = random.choice(["Kenya", "Bolivia", "Portugal", "Spain", "Scotland", "Thailand"])
    month = random.choice(["May", "June", "July", "April", "August", "September"])
    year = random.choice(["2023", "2024", "2025"])

    send_notification(
        event="toasts",
        subject="Trip Cancellation",
        message=f"The trip '{location} {month} {year}' has been cancelled.",
        ts=now(),
        template="demo/toast.html",
    )
    return render(request, "demo/send_event.html", {})


def sse(request: HttpRequest) -> HttpResponseBase:
    """Small demo of the basic idea of SSE without any redis or other complexity"""

    async def stream(request: HttpRequest) -> AsyncGenerator[str, None]:
        counter = 0
        while True:
            counter += 1
            await asyncio.sleep(5.0)
            yield f"data: <div>{counter}</div>\n\n"

    return StreamingHttpResponse(
        streaming_content=stream(request),
        content_type="text/event-stream",
    )


urlpatterns = [
    path("", index, name="home"),
    path("send/", send_event, name="send-event"),
    path("events/<str:event_name>/", events, name="events"),
    path("sse/", sse, name="basic-sse"),
]
