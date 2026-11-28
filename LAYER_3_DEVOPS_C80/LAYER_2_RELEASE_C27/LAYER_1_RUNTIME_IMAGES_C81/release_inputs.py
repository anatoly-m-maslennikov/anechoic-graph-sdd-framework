"""Compatibility alias for the package entry."""

import sys
from .input_selection import input_selection__shared as _entry

sys.modules[__name__] = _entry
