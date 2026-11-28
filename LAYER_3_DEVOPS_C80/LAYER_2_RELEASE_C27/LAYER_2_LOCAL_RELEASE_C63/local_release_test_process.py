"""Compatibility alias for the package implementation."""

import sys

from .release_environment._package__shared import local_release_test_process as _module

sys.modules[__name__] = _module
