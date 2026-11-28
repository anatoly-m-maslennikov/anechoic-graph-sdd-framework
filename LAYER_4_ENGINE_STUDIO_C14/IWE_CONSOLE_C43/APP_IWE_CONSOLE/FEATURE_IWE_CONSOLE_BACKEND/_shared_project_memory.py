import sys

from .workbench_queries.sessions._package__shared import _shared_project_memory as _module

sys.modules[__name__] = _module
