import sys

from .workbench_queries.sessions.server._package__shared import shared_backend_process as _module

if __name__ == "__main__":
    _module.main()
else:
    sys.modules[__name__] = _module
