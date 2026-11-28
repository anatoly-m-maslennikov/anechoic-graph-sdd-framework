import sys
from .kernel_model.audit_ingest.audit_ingest__shared import audit_storage as _module
sys.modules[__name__] = _module
