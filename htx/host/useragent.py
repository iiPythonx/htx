# Copyright (c) 2025 iiPython

# Modules
import re

# Handling
USERAGENT_COMPONENT = re.compile(r"(\w+\/[\d.]+)")
BROWSER_MAPPING = {
    "opr": "opera",
    "edg": "edge",
    "chrome": "chromium"
}

def transform(useragent: str) -> str:
    name, version = useragent.split("/")
    useragent = f"{BROWSER_MAPPING.get(name, name)}/{version.rstrip('.0')}"
    useragent =  useragent[:20] + "..." if len(useragent) > 20 else useragent
    return useragent + (" " * (23 - len(useragent)))

def clean_useragent(useragent: str) -> str:
    matches = USERAGENT_COMPONENT.findall(useragent)
    if len(matches) == 1:
        return transform(useragent.lower())  # This isn't a browser, ex. curl

    matches = matches[2:]  # Skip the Mozilla/ and engine components
    if matches[-2].startswith("Version/"):
        return transform(

            # Version/17.10 Safari/605.1.1 -> Safari/17.10
            f"{matches[-1].split('/')[0]}/{matches[-2].split('/')[1]}".lower()
        )

    return transform(matches[-(1 if "Safari" not in matches[-1] else 2)].lower())
