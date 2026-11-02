"""
Firebase Cloud Functions (2nd Gen) Python entrypoint.
Wraps the FastAPI ASGI application to serve REST API endpoints and Telegram webhooks.
"""

import asyncio
import threading
from firebase_functions import https_fn
from server import app

# Shared persistent event loop for handling async FastAPI requests across invocations
_loop = None
_thread = None


def get_event_loop() -> asyncio.AbstractEventLoop:
    global _loop, _thread
    if _loop is None:
        _loop = asyncio.new_event_loop()
        _thread = threading.Thread(target=_loop.run_forever, daemon=True)
        _thread.start()
    return _loop


@https_fn.on_request(memory=512, timeout_sec=60)
def api(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP entrypoint for Firebase Cloud Functions & Hosting rewrites.
    Routes requests through the FastAPI application.
    """
    loop = get_event_loop()

    # Translate Flask/Werkzeug request to ASGI scope
    scope = {
        "type": "http",
        "method": req.method,
        "path": req.path,
        "headers": [(k.lower().encode("latin1"), v.encode("latin1")) for k, v in req.headers.items()],
        "query_string": req.query_string,
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "server": (req.host.split(":")[0], 443),
        "scheme": req.headers.get("x-forwarded-proto", "https"),
    }
    body = req.get_data()

    async def call_asgi_app():
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        response_status = 200
        response_headers = []
        response_body = bytearray()

        async def send(message):
            nonlocal response_status, response_headers, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        await app(scope, receive, send)
        return response_status, response_headers, bytes(response_body)

    future = asyncio.run_coroutine_threadsafe(call_asgi_app(), loop)
    status, headers_list, res_body = future.result()

    headers_dict = {k.decode("latin1"): v.decode("latin1") for k, v in headers_list}
    return https_fn.Response(
        response=res_body,
        status=status,
        headers=headers_dict,
    )

