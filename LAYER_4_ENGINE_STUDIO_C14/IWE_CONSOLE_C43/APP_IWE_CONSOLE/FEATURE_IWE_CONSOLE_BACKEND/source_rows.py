import sys

from .source_capture._package__shared import source_rows as _module

sys.modules[__name__] = _module
