"""Source-bound graph bindings cases."""

from importlib import import_module
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(TOOL.parent))

_cases1 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.bindings._binding_cases_1"
)
_cases2 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.bindings._binding_cases_2"
)
_cases3 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.bindings._binding_cases_3"
)


class ContractGraphTests(
    _cases1.BindingCases1,
    _cases2.BindingCases2,
    _cases3.BindingCases3,
    unittest.TestCase,
):
    pass
