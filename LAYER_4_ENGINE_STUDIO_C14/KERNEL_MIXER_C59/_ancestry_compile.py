import sys
from .kernel_model.kernel_model__shared import _ancestry_compile as _module
sys.modules[__name__] = _module
