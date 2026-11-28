"""Source-bound graph native cases."""

from importlib import import_module
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(TOOL.parent))

_cases1 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.native._native_contract_cases_1"
)
_cases3 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.native._native_contract_cases_3"
)
_cases2 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.native._native_contract_cases_2"
)


class ContractGraphTests(
    _cases1.NativeContractCases1,
    _cases3.NativeContractCases3,
    _cases2.NativeContractCases2,
    unittest.TestCase,
):
    pass
