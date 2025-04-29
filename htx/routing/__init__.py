# Copyright (c) 2025 iiPython

# Modules
# from http import HTTPStatus
from htx.host import Host, Request, Response
from htx.reverse import ReverseProxy

# Application setup
async def scaffold_app(host: str, port: int) -> None:
    backend = Host()

    # Handle events
    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        return await ReverseProxy().request("http://localhost:8001", request)
        # return Response(
        #     HTTPStatus.OK,
        #     b"Hello, world!"
        # )

    await backend.start(host, port)
