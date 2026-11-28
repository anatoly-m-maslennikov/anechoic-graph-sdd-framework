import sys

from .workbench_queries.execution._package__shared import kernel_client as _module

sys.modules[__name__] = _module
