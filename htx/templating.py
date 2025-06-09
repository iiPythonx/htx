# Copyright (c) 2025 iiPython

from pathlib import Path

class Templating:
    def __init__(self, from_file: str) -> None:
        self.cache = {}
        self.source = Path(from_file).parent

    def fetch(self, id: str, **kwargs) -> bytes:
        if id not in self.cache:
            self.cache[id] = (self.source / f"{id}.html").read_text()

        return self.cache[id].format(**kwargs).encode("utf-8")
