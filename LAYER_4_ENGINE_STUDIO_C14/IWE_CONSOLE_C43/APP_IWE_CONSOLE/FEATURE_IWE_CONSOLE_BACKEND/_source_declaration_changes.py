import sys

from .source_capture._package__shared import _source_declaration_changes as _module

sys.modules[__name__] = _module
