import sys
from .kernel_graph.kernel_graph__shared import graph_store as _module
sys.modules[__name__] = _module
