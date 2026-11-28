"""Compatibility alias for the package entry."""

import sys
from .image_container import image_container__shared as _entry

sys.modules[__name__] = _entry
