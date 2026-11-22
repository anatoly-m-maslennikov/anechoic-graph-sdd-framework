"""Read the Framework stack packaged alongside the Engine."""

from functools import lru_cache
from pathlib import Path
import tomllib


@lru_cache(maxsize=1)
def runtime_stack():
    carrier = Path(__file__).resolve().parents[3] / "project.toml"
    try:
        document = tomllib.loads(carrier.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "current"
    if document not in ({"stack": "current"}, {"stack": "beta"}):
        raise ValueError("Invalid Framework stack")
    return document["stack"]
