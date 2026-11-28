"""Compatibility alias for the package implementation."""

import sys

from .release_environment._package__shared import local_release_gate_flow as _module

sys.modules[__name__] = _module
