# Copyright (c) 2025 iiPython

from pathlib import Path

class Templating:
    def __init__(self) -> None:
        self.cache = {}
        self.source = Path(__file__).parent

    def fetch(self, id: str, **kwargs) -> bytes:
        if id not in self.cache:
            self.cache[id] = (self.source / f"{id}.html").read_text()

        return self.cache[id].format(**kwargs).encode("utf-8")

templates = Templating()
