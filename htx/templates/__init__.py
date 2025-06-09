# Copyright (c) 2025 iiPython

# Modules
import re
from pathlib import Path

# Initialization
class NoSuchTemplate(Exception):
    pass

REPLACE_PATTERN = re.compile(r"%(\w+)")

# Main class
class Templating:
    def __init__(self, tree: list[Path]) -> None:
        self.cache = {}

        # Populate tree
        self.list = {}
        for path in tree + [Path(__file__).parent]:
            for file in path.iterdir():
                if file.suffix != ".html":
                    continue

                self.list[file.with_suffix("").name] = file

    def fetch(self, id: str, **kwargs) -> bytes:
        if id not in self.list:
            print(self.list)
            raise NoSuchTemplate

        if id not in self.cache:
            self.cache[id] = self.list[id].read_text()

        return REPLACE_PATTERN.sub(lambda m: kwargs.get(m.group(1), m.group(0)), self.cache[id]).encode("utf-8")
