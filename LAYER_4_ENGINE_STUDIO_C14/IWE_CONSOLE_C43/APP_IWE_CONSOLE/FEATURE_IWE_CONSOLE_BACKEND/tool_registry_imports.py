import sys

from .tool_registry._package__shared import tool_registry_imports as _module

sys.modules[__name__] = _module
