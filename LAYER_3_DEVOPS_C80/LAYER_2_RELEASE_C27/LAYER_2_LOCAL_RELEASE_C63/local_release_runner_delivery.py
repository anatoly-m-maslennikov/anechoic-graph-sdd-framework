"""Compatibility alias for the package implementation."""

import sys

from .release_execution._package__shared import local_release_runner_delivery as _module

sys.modules[__name__] = _module
