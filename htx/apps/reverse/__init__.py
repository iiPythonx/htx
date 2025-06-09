# Copyright (c) 2025 iiPython

# Modules
from http import HTTPStatus
from urllib.request import urlopen, Request as HTTPRequest
from urllib.error import HTTPError, URLError

from htx.host import Request, Response
from htx.templates import Templating

# Main class
class ReverseProxy:
    def __init__(self) -> None:
        self.templating = Templating([])

    async def request(self, base_url: str, request: Request) -> Response:
        try:
            with urlopen(HTTPRequest(f"{base_url}{request.path}", headers = request.headers, data = request.body, method = request.method)) as response:
                return Response(response.status, response.read(), {n: v for n, v in response.getheaders()})

        except HTTPError as e:
            return Response(e.code, e.read(), {n: v for n, v in e.headers.items()})

        except URLError as e:
            return Response(
                HTTPStatus.BAD_GATEWAY,
                self.templating.fetch("error", title = "BAD GATEWAY", message = e.reason)
            )

        except Exception as e:
            return Response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                self.templating.fetch("error", title = "INTERNAL PROXYING ISSUE", message = f"The HTX backend failed to exchange your request.<br>{e}")
            )

