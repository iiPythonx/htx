# Copyright (c) 2025 iiPython

# Modules
import argparse
from http import HTTPStatus
from urllib.request import urlopen, Request as HTTPRequest
from urllib.error import HTTPError, URLError

from htx.host import Request, Response, Host
from htx.templates import Templating

# Application setup
def scaffold_app(backend: Host, cmd: list[str]) -> None:

    # Parse arguments
    p = argparse.ArgumentParser(prog = "htx.apps.reverse", add_help = False)
    p.add_argument("upstream")
    args, _ = p.parse_known_args(cmd)

    # Setup templating
    templates = Templating([])

    # Request handling
    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        try:
            request.headers["host"] = args.upstream.split("://")[1].strip("/")
            with urlopen(HTTPRequest(f"{args.upstream}{request.path}", headers = request.headers, data = request.body, method = request.method)) as response:
                return Response(response.status, response.read(), {n: v for n, v in response.getheaders()})

        except HTTPError as e:
            return Response(e.code, e.read(), {n: v for n, v in e.headers.items()})

        except URLError as e:
            return Response(
                HTTPStatus.BAD_GATEWAY,
                templates.fetch("error", title = "BAD GATEWAY", message = e.reason)
            )

        except Exception as e:
            return Response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                templates.fetch("error", title = "INTERNAL PROXYING ISSUE", message = f"The HTX backend failed to exchange your request.<br>{e}")
            )
