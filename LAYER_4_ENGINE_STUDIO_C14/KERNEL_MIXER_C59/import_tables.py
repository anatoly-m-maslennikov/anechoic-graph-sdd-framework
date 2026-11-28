import sys
from .kernel_services.native_projection.native_projection__shared import import_tables as _module
sys.modules[__name__] = _module
