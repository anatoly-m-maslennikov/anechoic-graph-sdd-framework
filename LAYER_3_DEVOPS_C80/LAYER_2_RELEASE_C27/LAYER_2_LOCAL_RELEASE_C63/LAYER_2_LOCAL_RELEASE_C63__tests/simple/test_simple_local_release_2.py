"""The concrete Local release flow with fake release operations."""

import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.second import _simple_release_two_cases_1 as cases1
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.second import _simple_release_two_cases_2 as cases2
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.simple.second import _simple_release_two_cases_3 as cases3
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import LAYER_2_LOCAL_RELEASE_C63__tests__shared as shared


class SimpleLocalReleaseTests(
    cases1.SimpleReleaseTwoCases1,
    cases2.SimpleReleaseTwoCases2,
    cases3.SimpleReleaseTwoCases3,
    shared.SimpleReleaseFixture,
    unittest.TestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
