"""Compatibility alias for the package implementation."""

import sys

from .release_state._package__shared import local_release_previous as _module

sys.modules[__name__] = _module
