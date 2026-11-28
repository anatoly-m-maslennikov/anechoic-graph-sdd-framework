"""Compatibility alias for the package entry."""

import sys
from .image_builder import image_builder__shared as _entry

sys.modules[__name__] = _entry
