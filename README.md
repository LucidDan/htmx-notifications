htmx-notifications
------------------

This project provides a sample django project called 'demo', designed to showcase some functionality from the DjangoCon AU
talk "Using Django 4.2's StreamingHttpResponse and HTMX SSE to provide real time notifications".

In particular, it demonstrates three different functionalities:
1. A demonstration of how StreamingHttpResponse can be used to deliver broadcast messages for a particular session.
2. A demonstration of how StreamingHttpResponse can be used with a simple model to keep track of notifications for a user, and see updates in real time.
3. A demonstration of how an existing StreamingHttpResponse can leverage multi-target htmx to update other things on the page, like a form when a notification is received.

The project has been set up to also demonstrate several ways of handling enqueued messages:
1. Simplistic asyncio Queue(); only works in a single-threaded, single-process ASGI web server.
2. Redis pubsub; works with multiple processes, scales fairly well.
3. Postgres LISTEN/NOTIFY; works with multiple processes; does not scale very well unless you have a big PG server/bouncer.
4. DB model for notifications, with a cache flag to indicate when there is new data to send. Scales much better.

Other challenges:
- Every active user that leaves a page open maintains an SSE connection. There's no real way to detect that the page is
  inactive...so you can easily end up with too many connections open for all the (possibly idle) pages.
- Some error handling is a good idea. You might even need/want some javascript, despite the use of HTMX.
- Acknowledgement that a notification was rendered to the user, not just received over SSE but never displayed, is tricky. Despite the extra load, it might be worth POST-ing to indicate that the message is being received and rendered.
- If you need to run under WSGI for some reason, you're (mostly?) out of luck.
- 
