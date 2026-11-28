import sys

from .workbench_queries._package__shared import query_templates as _module

sys.modules[__name__] = _module
