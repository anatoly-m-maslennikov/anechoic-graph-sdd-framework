"""Keep resumed release effects on the original Docker context."""

import json
import unittest
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)
from ..LAYER_2_LOCAL_RELEASE_C63__tests__shared import SimpleReleaseFixture


class ResumeDockerContextTests(SimpleReleaseFixture, unittest.TestCase):
    def test_context_binding_and_legacy_journal(self):
        runner, _ = self._runner()
        options = {"run_id": "engine-context", "runner": runner}
        journal = self.root / (
            ".anechoic_runtime/simple_local_release/runs/engine-context/st"
            "ate.json"
        )
        with patch.dict("os.environ", {"DOCKER_CONTEXT": "orbstack"}):
            completed = run_local_release(self.root, **options)
            self.assertEqual("completed", completed["outcome"], completed)
            self.assertEqual(
                "orbstack", json.loads(journal.read_text())["docker_context"]
            )
        with patch.dict("os.environ", {"DOCKER_CONTEXT": "desktop-linux"}):
            blocked = run_local_release(self.root, resume=True, **options)
            self.assertEqual(
                "local-release-resume-docker-context-changed", blocked["error"]
            )
            data = json.loads(journal.read_text())
            del data["docker_context"]
            journal.write_text(json.dumps(data))
            legacy = run_local_release(self.root, resume=True, **options)
            self.assertEqual("completed", legacy["outcome"], legacy)


if __name__ == "__main__":
    unittest.main()
