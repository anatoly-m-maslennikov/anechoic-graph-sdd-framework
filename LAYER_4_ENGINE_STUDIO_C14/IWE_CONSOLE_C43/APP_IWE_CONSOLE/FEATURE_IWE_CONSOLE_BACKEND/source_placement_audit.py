import sys

from .source_audit._package__shared import source_placement_audit as _module

sys.modules[__name__] = _module
