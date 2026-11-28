"""Generated native lifecycle paths; each case uses a fresh project."""

from pathlib import Path
import sys
import unittest

sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[4]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.lifecycle_route_support import (  # noqa: E402
    LifecycleRouteSupport,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.routing.asset_routes import (  # noqa: E402
    _lifecycle_spec_asset_cases_1 as cases1,
    _lifecycle_spec_asset_cases_2 as cases2,
    _lifecycle_spec_asset_cases_3 as cases3,
)

Model = cases1.Model


class LifecycleRouteMatrix(
    cases1.LifecycleSpecAssetCases1,
    cases2.LifecycleSpecAssetCases2,
    cases3.LifecycleSpecAssetCases3,
    LifecycleRouteSupport,
    unittest.TestCase,
):
    pass
