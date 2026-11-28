import sys

from .source_capture.reader._package__shared import source_reader as _module

sys.modules[__name__] = _module
