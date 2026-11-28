"""The concrete Local release flow with fake release operations."""

import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.third import _simple_release_three_cases_1 as cases1
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.third import _simple_release_three_cases_2 as cases2
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import LAYER_2_LOCAL_RELEASE_C63__tests__shared as shared


class SimpleLocalReleaseTests(
    cases1.SimpleReleaseThreeCases1,
    cases2.SimpleReleaseThreeCases2,
    shared.SimpleReleaseFixture,
    unittest.TestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
