import unittest

from ._trace_spec_support import transition as transition
from ._trace_spec_implication_cases import _TraceImplicationCases
from ._trace_spec_rejection_cases import _TraceRejectionCases
from ._trace_spec_binding_cases import _HttpCases


class TraceSpecTests(
    _TraceImplicationCases, _TraceRejectionCases, unittest.TestCase
):
    pass


class HttpBindingTests(_HttpCases, unittest.TestCase):
    pass
