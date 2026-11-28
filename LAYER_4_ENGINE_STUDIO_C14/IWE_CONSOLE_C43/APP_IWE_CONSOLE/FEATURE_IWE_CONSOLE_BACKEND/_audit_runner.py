import sys

from .source_audit._package__shared import _audit_runner as _module

sys.modules[__name__] = _module
