import sys
from .kernel_runtime.kernel_runtime__shared import query_log as _module
sys.modules[__name__] = _module
