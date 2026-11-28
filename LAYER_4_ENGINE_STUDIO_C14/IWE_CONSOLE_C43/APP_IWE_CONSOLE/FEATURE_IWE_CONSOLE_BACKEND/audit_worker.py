import sys

from .source_audit._package__shared import audit_worker as _module

sys.modules[__name__] = _module
