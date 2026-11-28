"""Compatibility alias for the package implementation."""

import sys

from .release_preparation._package__shared import local_release_package_phases as _module

sys.modules[__name__] = _module
