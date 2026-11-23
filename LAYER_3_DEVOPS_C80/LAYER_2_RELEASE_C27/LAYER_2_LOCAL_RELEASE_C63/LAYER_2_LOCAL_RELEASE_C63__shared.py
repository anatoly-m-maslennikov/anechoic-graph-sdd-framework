"""Project Local Release interface."""

from . import local_release
from .local_release import run_local_release
from .release_support import _GENERATED_ASSETS

__all__ = [
    "run_local_release", "local_release", "_GENERATED_ASSETS",
]
