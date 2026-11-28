"Local Release resume through the public entry point with temporary targets."

import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.lifecycle import _local_release_resume_cases_1 as cases1
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.lifecycle import _local_release_resume_cases_2 as cases2
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.lifecycle import _local_release_resume_cases_3 as cases3
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import LAYER_2_LOCAL_RELEASE_C63__tests__shared as shared


class LocalReleaseResumeTests(
    cases1.LocalReleaseResumeCases1,
    cases2.LocalReleaseResumeCases2,
    cases3.LocalReleaseResumeCases3,
    shared.SimpleReleaseFixture,
    unittest.TestCase,
):
    run_id = "resumable-release"


if __name__ == "__main__":
    unittest.main()
