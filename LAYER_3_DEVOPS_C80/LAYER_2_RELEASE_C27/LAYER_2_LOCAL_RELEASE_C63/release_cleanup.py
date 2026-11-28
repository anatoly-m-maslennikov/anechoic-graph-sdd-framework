"""Compatibility alias for the package implementation."""

import sys

from .release_cleanup_ops._package__shared import release_cleanup as _module

sys.modules[__name__] = _module
