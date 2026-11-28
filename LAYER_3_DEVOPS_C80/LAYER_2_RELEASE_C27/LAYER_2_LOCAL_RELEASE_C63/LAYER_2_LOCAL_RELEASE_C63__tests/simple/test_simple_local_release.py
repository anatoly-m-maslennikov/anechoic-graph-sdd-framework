"""The concrete Local release flow with fake release operations."""

import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.first import _simple_release_cases_1 as cases1
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.first import _simple_release_cases_2 as cases2
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.first import _simple_release_cases_3 as cases3
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import LAYER_2_LOCAL_RELEASE_C63__tests__shared as shared


class SimpleLocalReleaseTests(
    cases1.SimpleReleaseCases1,
    cases2.SimpleReleaseCases2,
    cases3.SimpleReleaseCases3,
    shared.SimpleReleaseFixture,
    unittest.TestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
