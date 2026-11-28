import sys

from .workbench_queries.execution.process._package__shared import backend_process as _module

if __name__ == "__main__":
    _module.main()
else:
    sys.modules[__name__] = _module
