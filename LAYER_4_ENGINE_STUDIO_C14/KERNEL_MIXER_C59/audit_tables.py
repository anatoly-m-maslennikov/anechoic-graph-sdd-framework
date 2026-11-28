import sys
from .kernel_model.audit_ingest.audit_ingest__shared import audit_tables as _module
sys.modules[__name__] = _module
