import sys
from .kernel_services.kernel_services__shared import _interface_dispatch as _module
sys.modules[__name__] = _module
