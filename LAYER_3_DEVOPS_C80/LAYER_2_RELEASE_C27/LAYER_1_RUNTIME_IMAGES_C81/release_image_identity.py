"""Compatibility alias for the package entry."""

import sys
from .image_identity import image_identity__shared as _entry

sys.modules[__name__] = _entry
