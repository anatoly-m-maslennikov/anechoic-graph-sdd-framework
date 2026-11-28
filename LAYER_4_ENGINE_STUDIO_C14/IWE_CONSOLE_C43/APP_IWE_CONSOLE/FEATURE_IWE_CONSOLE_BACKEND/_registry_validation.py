import sys

from .tool_registry.validation._package__shared import _registry_validation as _module

sys.modules[__name__] = _module
