# Copyright (c) 2025 iiPython

# Modules
from htx.host import Host, Request, Response

# Application setup
async def scaffold_app(host: str, port: int) -> None:
    backend = Host()

    # Handle events
    @backend.event("request")
    async def on_request(request: Request) -> Response:
        return Response(
            code = 200,
            body = b"<!doctype html><html><body><p>This site is powered by <b>HTX</b>.</p></body></html>",
            head = {
                "Content-Type": "text/html"
            }
        )

    await backend.start(host, port)
