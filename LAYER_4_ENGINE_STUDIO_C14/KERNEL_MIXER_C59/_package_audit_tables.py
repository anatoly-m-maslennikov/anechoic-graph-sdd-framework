import sys
from .kernel_services.kernel_services__shared import _package_audit_tables as _module
sys.modules[__name__] = _module
