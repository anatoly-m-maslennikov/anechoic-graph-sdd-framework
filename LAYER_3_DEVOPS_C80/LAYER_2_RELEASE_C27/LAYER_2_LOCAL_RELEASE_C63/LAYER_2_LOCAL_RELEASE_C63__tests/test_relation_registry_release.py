"""Release requires the checked-in tool registry before running its gates."""

import unittest

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import (
    test_simple_local_release as release_fixture,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    local_release,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    _GENERATED_ASSETS,
)


class RelationRegistryReleaseTests(unittest.TestCase):
    def setUp(self):
        self.fixture = release_fixture.SimpleLocalReleaseTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_missing_registry_stops_before_tests_or_image_build(self):
        fixture = self.fixture
        (fixture.root / next(iter(_GENERATED_ASSETS))).unlink()
        runner, calls = fixture._runner()
        result = local_release.run_local_release(
            fixture.root, run_id="tool-registry-missing", runner=runner
        )
        self.assertEqual(
            ("failed", "validate_inputs"),
            (result["outcome"], result["failed_step"]),
        )
        self.assertFalse(any(argv[0] == "uv" for argv in calls))
        fixture.image_factory.assert_not_called()
        fixture.start_container.assert_not_called()

    def test_invalid_registry_stops_before_tests_or_image_build(self):
        fixture = self.fixture
        registry = fixture.root / next(iter(_GENERATED_ASSETS))
        for content in ("not-json", "[]", "null"):
            with self.subTest(content=content):
                registry.write_text(content, encoding="utf-8")
                runner, calls = fixture._runner()
                result = local_release.run_local_release(
                    fixture.root, run_id="tool-registry-invalid", runner=runner
                )
                self.assertEqual(
                    ("failed", "validate_inputs"),
                    (result["outcome"], result["failed_step"]),
                )
                self.assertFalse(any(argv[0] == "uv" for argv in calls))
                fixture.image_factory.assert_not_called()
                fixture.start_container.assert_not_called()


if __name__ == "__main__":
    unittest.main()
