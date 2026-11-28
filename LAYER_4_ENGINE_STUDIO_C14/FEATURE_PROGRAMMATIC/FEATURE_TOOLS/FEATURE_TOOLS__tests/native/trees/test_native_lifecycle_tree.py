from pathlib import Path
import sys
import unittest


sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[3]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.native_lifecycle_update_support import (
    NativeUpdateSupport,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.trees import (  # noqa: E402
    _native_tree_cases_1 as cases1,
    _native_tree_cases_2 as cases2,
    _native_tree_cases_3 as cases3,
)


class NativeDirectUpdateTests(
    cases1.NativeTreeCases1,
    cases2.NativeTreeCases2,
    cases3.NativeTreeCases3,
    NativeUpdateSupport,
    unittest.TestCase,
):
    pass
