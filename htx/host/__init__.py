# Copyright (c) 2025 iiPython

# Modules
import re
import typing
import asyncio
from enum import Enum
from http import HTTPStatus
from time import perf_counter
from urllib.parse import unquote
from dataclasses import dataclass

from htx import __version__

# Exceptions
class InvalidRequest(Exception):
    pass

# Expressions
HTTP_PROTOCOL = re.compile(rb"(GET|POST|PATCH|DELETE|PUT|TRACE) (\/(?:[^?]+)?)(\?[\w\d\%\&\=]+)? HTTP\/(\d(?:.{2,3})?)")
HTTP_HEADER   = re.compile(rb"([\w-]+): (.+)")

# Typing
class ReadMode(Enum):
    INCOMING_HEADERS = 1
    INCOMING_BODY    = 2
    REQUEST_DONE     = 3

class Response:
    def __init__(self, code: HTTPStatus | int, body: bytes, head: dict[str, str] = {}) -> None:
        self.code, self.body, self.head = code, body, head

@dataclass
class Request:
    method:  str
    path:    str
    query:   str
    version: str
    headers: dict[str, str]
    body:    bytes
    client:  tuple[str, int]

    def log(self) -> typing.Callable:
        start = perf_counter()
        def end_log(status_code: int | None) -> None:
            path = f"{self.path}{self.query}"
            path = path[:50] + "..." if len(path) > 50 else path
            path += (" " * (53 - len(path)))

            code = f"\033[3{1 if status_code > 400 else 2}m{status_code}" if isinstance(status_code, int) else "\033[90m---"

            print(f"\033[90m[ {self.client[0]} ] \033[34m{self.method} {path} {code} \033[90m[\033[34m{round((perf_counter() - start) * 1000, 1)}ms\033[90m]\033[0m")

        return end_log

class IncomingRequest:
    def __init__(self) -> None:
        self.mode: ReadMode = ReadMode.INCOMING_HEADERS
        self.buffer: bytes = b""

        # Request data
        self.protocol: list[str] = []
        self.headers: dict[str, str] = {}

    def build(self) -> None:
        self.body = self.buffer
        self.mode = ReadMode.REQUEST_DONE

    def process_chunks(self, chunks: list[bytes]) -> None:
        http_match = HTTP_PROTOCOL.match(chunks[0])
        if http_match is None:
            raise InvalidRequest

        self.protocol = [unquote((piece or b"").decode()) for piece in http_match.groups()]

        # Process headers
        for chunk in chunks[1:]:
            header_match = HTTP_HEADER.match(chunk)
            if header_match is None:
                raise InvalidRequest

            name, value = header_match.groups()
            self.headers[name.decode().lower()] = value.decode()

        self.mode = ReadMode.INCOMING_BODY

    def extend(self, chunk: bytes) -> None:
        self.buffer += chunk
        buffer_size = len(self.buffer)

        # Check for end of HTTP headers
        if b"\r\n\r\n" in self.buffer and self.mode == ReadMode.INCOMING_HEADERS:
            http_section, request_body = self.buffer.split(b"\r\n\r\n")
            self.process_chunks(http_section.split(b"\r\n"))

            # Handle updating buffer
            self.buffer = request_body
            if "content-length" not in self.headers:
                return self.build()  # If this request has no Content-Length, assuming we're done after the headers

        # Handle possible body (if there is one)
        elif self.mode == ReadMode.INCOMING_BODY:
            if buffer_size == 0:
                return self.build()

            if not self.headers.get("content-length", "").isnumeric():
                raise InvalidRequest

            content_length = int(self.headers["content-length"])
            if buffer_size == content_length:
                return self.build()

    def dump(self, peer: tuple[str]) -> Request:
        return Request(
            *self.protocol,  # type: ignore
            self.headers,    # type: ignore
            self.body,       # type: ignore
            peer[:2]         # type: ignore
        )

# Main handling
class Host:
    def __init__(self) -> None:
        self.events: dict[str, list[typing.Callable]] = {}

    @staticmethod
    def _dump_response(response: Response) -> bytes:
        response.head = {k.lower(): v for k, v in response.head.items()} | {
            "connection": "close",
            "content-length": str(len(response.body)),
            "server": f"htx/{__version__}"
        }
        return b"\r\n".join([
            f"HTTP/1.1 {response.code}".encode(),
            *[f"{name}: {value}".encode() for name, value in response.head.items()],
            b"\r\n" + response.body
        ])

    async def _handle_client(self, read: asyncio.StreamReader, write: asyncio.StreamWriter) -> None:
        request = IncomingRequest()
        while True:
            result = await read.read(20)
            if not result:
                break

            request.extend(result)
            if request.mode == ReadMode.REQUEST_DONE:
                break

        # Broadcast event
        response, request = None, request.dump(write.get_extra_info("peername"))

        log = request.log()
        for listener in self.events.get("request", []):
            response = await listener(request)  # First come, first server
            if response is not None:
                break

        if response:
            if not isinstance(response, (Response, bytes)):
                raise ValueError("Returned value must be either a :Response: object or bytes!")

            log(response.code if isinstance(response, Response) else None)
            write.write(self._dump_response(response) if isinstance(response, Response) else response)
            await write.drain()

        write.close()
        await write.wait_closed()

    async def start(self, host: str, port: int) -> None:
        """Start the HTTP backend, listening on the specified host and port."""
        async with await asyncio.start_server(self._handle_client, host, port) as socket:
            await socket.serve_forever()

    # Handle events
    def add_event(self, event: str, callback: typing.Callable) -> None:
        """Add an event listener for the specified callback. This method
        can be stacked multiple times, across multiple different functions."""

        if event not in self.events:
            self.events[event] = []

        if callback in self.events[event]:
            return

        self.events[event].append(callback)

    def del_event(self, event: str, callback: typing.Callable) -> None:
        """Remove an event listener for the specified callback. If the callback
        does not already have an event listener, this function will do nothing."""

        if event not in self.events:
            return

        if callback in self.events[event]:
            self.events[event].remove(callback)

    def event(self, event: str) -> typing.Callable:
        """Shortcut decorator version of :Host:.add_event(), requires event name
        to bind to."""

        def internal_callback(callback: typing.Callable) -> None:
            self.add_event(event, callback)

        return internal_callback
