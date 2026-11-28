import sys

from .workbench_queries.sessions.config._package__shared import host_runtime_config as _module

if __name__ == "__main__":
    raise SystemExit(_module.main())
else:
    sys.modules[__name__] = _module
