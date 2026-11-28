import sys

from .source_capture._package__shared import source_reader_capture as _module

sys.modules[__name__] = _module
