from contextlib import redirect_stderr as redirect_stderr
from hashlib import sha256 as sha256
from io import StringIO as StringIO
import json as json
import os as os
from pathlib import Path as Path
from time import monotonic as monotonic
import unittest
from unittest.mock import patch as patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext as ReadContext,
    capture_ticket_delta as capture_ticket_delta,
    native_carrier_hashes as native_carrier_hashes,
    prepare_generation_snapshot as prepare_generation_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native as capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_status_domains import (
    status_domains as status_domains,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
        NativeCaptureFixture,
    )  # fmt: skip

from ._native_generation_staged_cases import NativeGenerationStagedCases
from ._native_generation_archive_cases import NativeGenerationArchiveCases
from ._native_generation_misc_cases import NativeGenerationMiscCases


class NativeGenerationTests(
    NativeGenerationStagedCases,
    NativeGenerationArchiveCases,
    NativeGenerationMiscCases,
    NativeCaptureFixture,
    unittest.TestCase,
):
    pass
