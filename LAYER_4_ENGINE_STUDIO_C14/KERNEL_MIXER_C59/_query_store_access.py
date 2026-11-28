import sys
from .kernel_query.query_database.query_database__shared import _query_store_access as _module
sys.modules[__name__] = _module
