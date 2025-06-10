<div align = "center">

![HTX Logo](.github/htx.png)

A built from scratch Python HTTP server with custom apps.

</div>

### Synopsis

HTX is a zero-dependency HTTP server built entirely from scratch as an experiment/proof of concept. It can act as a standalone HTTP server, giving low level access to the protocol, and also has the ability to load custom "ASGI" applications.

### Basic usage

#### HTTP

```py
import asyncio
from http import HTTPStatus

from htx.host import Host, Request, Response

backend = Host()

@backend.event("request")
async def on_request(request: Request) -> Response:
    return Response(
        HTTPStatus.OK,
        b"Hello, world!"
    )

asyncio.run(backend.start(host, port))
```

The only current event is `request`; however, depending on whether SSL termination gets added there may be more down the road.

#### Shell CLI

HTX supports being given a Python module name and then loading it as a custom application. Some built-in apps include:
- Reverse Proxying
    - `htx htx.apps.reverse https://google.com`
- File Listing
    - `htx htx.apps.serve /etc/data`

The basic structure of such an app should follow this design:
```py
from htx.host import Host, Request, Response

def scaffold_app(backend: Host, cmd: list[str]) -> None:

    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        return Response(200, b"OK")
```

`cmd` is a list of command arguments, which can be passed to `argparse.ArgumentParser.parse_known_args`.

### Typing

The main types of this library are as follows:

```py
type Request {
    method:  str
    path:    str
    query:   str
    version: str              # HTTP version in use
    headers: dict[str, str]
    body:    bytes
    client:  tuple[str, int]  # Tuple of (hostname, port)
}

type Response {
    code: HTTPStatus | int
    body: bytes
    head: dict[str, str] = {}
}
```

These types can be assumed to be constant and more then likely won't be changed even as the API progresses.  
If you are using HTX and have a situation where the API is not typed very intuitively, please open a issue.

### General notice

This module is built for fun and research about HTTP in general. By no means is it code that should be deployed in production, whether for laughs or otherwise.  
If you do find any sort of security vulnerability, please feel free to open an issue for it. Confidentiality is not a requirement in this case.
