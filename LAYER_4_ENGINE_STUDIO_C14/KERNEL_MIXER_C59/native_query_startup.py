import sys
from .kernel_runtime.kernel_runtime__shared import native_query_startup as _module
sys.modules[__name__] = _module
