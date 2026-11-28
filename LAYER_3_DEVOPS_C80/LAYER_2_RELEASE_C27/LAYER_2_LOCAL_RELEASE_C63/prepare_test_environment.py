"""Compatibility alias for the package implementation."""

import sys

from .release_environment._package__shared import prepare_test_environment as _module

sys.modules[__name__] = _module
