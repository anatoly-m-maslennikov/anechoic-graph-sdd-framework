"""Compatibility alias for the package implementation."""

import sys

from .release_state._package__shared import snapshot_inputs as _module

sys.modules[__name__] = _module
