import sys
from .kernel_query.query_database.query_database__shared import query_store as _module
sys.modules[__name__] = _module
