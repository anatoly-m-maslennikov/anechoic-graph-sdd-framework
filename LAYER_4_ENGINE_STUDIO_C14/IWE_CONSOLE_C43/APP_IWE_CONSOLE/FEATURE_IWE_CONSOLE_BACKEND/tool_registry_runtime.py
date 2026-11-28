import sys

from .tool_registry.validation._package__shared import tool_registry_runtime as _module

sys.modules[__name__] = _module
