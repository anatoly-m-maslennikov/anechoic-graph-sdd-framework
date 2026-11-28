"""Verify framing in the complete formal chain."""

import os
import shutil
import unittest

from ._direct_framing_observations import (
    CONTRACT as CONTRACT,
    SOLUTION as SOLUTION,
    FramingObservationCases,
    framing_pins as framing_pins,
)
from ._direct_framing_workflows import FramingWorkflowCases


class DirectFramingChainTests(
    FramingObservationCases, FramingWorkflowCases, unittest.TestCase
):
    def setUp(self):
        self.lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(self.lean, "Lean executable unavailable")
