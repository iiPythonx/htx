# Copyright (c) 2025 iiPython

# Metadata
__requires__ = ["natsort>=8.4.0"]

# Modules
import stat
import argparse
import mimetypes
from pathlib import Path

from natsort import natsorted  # pyright: ignore

from htx import __version__
from htx.host import Host, Request, Response
from htx.templates import Templating

# Handle byte suffixes
def cleanup(num: int | float) -> str:
    unit = ""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if num < 1000 - 0.5:
            break

        if unit != "YB":
            num /= 1000

    return "{:.0f}{}".format(num, unit)

# Application setup
def scaffold_app(backend: Host, cmd: list[str]) -> None:
    active_cache = {}

    # Parse arguments
    p = argparse.ArgumentParser(prog = "htx.apps.serve", add_help = False)
    p.add_argument("path")
    args, _ = p.parse_known_args(cmd)

    # Setup templating
    path = Path(args.path)
    templates = Templating([Path(__file__).parent / "templates"])

    # Request handling
    @backend.event("request")
    async def on_request(request: Request) ->  Response:
        target = path / request.path[1:]
        if not target.exists():
            return Response(404, templates.fetch("error", title = "NOT FOUND", message = "Please check your URL and try again."))

        if target.is_dir():
            modified_time = target.stat().st_ctime
            if target not in active_cache or active_cache[target]["modified"] != modified_time:
                directories, files = [], []
                for item in target.iterdir():
                    name = item.name  # Grab name prior to resolve

                    # Resolve any potential symlinks
                    item = item.resolve()
                    if not item.exists():
                        continue  # And if it's a bad link, then ignore it

                    file = item.stat()
                    (directories if item.is_dir() else files).append((name, cleanup(file.st_size) if item.is_file() else 0, item.relative_to(path), stat.filemode(file.st_mode)))

                size_html, name_html, perm_html = "", "", ""
                for category in [directories, files]:
                    for name, size, relative, perm in natsorted(category, key = lambda _: _[0]):
                        size_html += f"<span>{size}</span>"
                        name_html += f"<span><a href = \"/{relative}\">{name}</a></span>"
                        perm_html += f"<span>{perm}</span>"

                active_cache[target] = {
                    "modified": modified_time,
                    "data": {"size": size_html, "name": name_html, "perm": perm_html}
                }

            return Response(
                200,
                templates.fetch(
                    "listing",
                    **active_cache[target]["data"],
                    version = __version__,
                    current = str(target.relative_to(path)) if target != path else ""
                )
            )

        mime_type, _ = mimetypes.guess_type(target.name)
        return Response(200, target.read_bytes(), {"Content-Type": mime_type or "application/octet-stream"})
