"""Compatibility alias for the package implementation."""

import sys

from .release_preparation._package__shared import prepare_local as _module

sys.modules[__name__] = _module
