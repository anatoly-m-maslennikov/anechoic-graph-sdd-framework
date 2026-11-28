import sys
from .kernel_query.kernel_query__shared import query_results as _module
sys.modules[__name__] = _module
