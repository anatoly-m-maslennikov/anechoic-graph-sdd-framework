"""Shared fixture actions for snapshot release fix-cycle tests."""

import json
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    SnapshotReleaseRun,
    test_environment as gate_environment,
)

_CANARY = "verify candidate canary"


class SnapshotFixActions:
    @property
    def state(self):
        return self.runtime / "simple_local_release/runs/snapshot/state.json"

    def journal(self):
        return json.loads(self.state.read_text())

    def fix(self, path, content):
        file = self.source / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        self.git(self.source, "add", "--", path.as_posix())
        self.git(self.source, "commit", "-qm", f"Fix {path.name}")
        self.source_revision = self.git(
            self.source, "rev-parse", "HEAD"
        ).strip()
        return self.source_revision

    def attempt(self, failed_phase=None, *, resume=True):
        self.calls.clear()
        self.fail_phase = failed_phase
        return self.release(resume=resume)

    def stop_before_claim(self):
        with patch.object(
            SnapshotReleaseRun,
            "_before_delivery",
            side_effect=LocalReleaseError("stop before claim"),
        ):
            result = self.attempt(resume=False)
        self.assertEqual("stop before claim", result["error"], result)
        self.assertNotIn("delivery", self.journal())

    def schema_one(self):
        journal = self.journal()
        journal.update(
            schema=1, inputs=[self.source_revision, list(gate_environment())]
        )
        for field in (
            "proofs",
            "canary_inputs",
            "accepted_source_sha",
            "build_source_sha",
        ):
            journal.pop(field, None)
        if _CANARY in journal["done"]:
            journal["done"].remove(_CANARY)
        self.state.write_text(json.dumps(journal))

    def test_failed_startup_keeps_its_bounded_diagnostics_after_resume(self):
        error = LocalReleaseError("fixture startup failure")
        error.add_note("Local Release startup diagnostics: " + "x" * 5000)
        error.add_note("not a startup diagnostic")
        self.start_container.side_effect = error
        failed = self.attempt(resume=False)
        self.assertEqual("start_mcp", failed["failed_step"], failed)
        observed = failed["diagnostics"]
        self.assertEqual([4096], [len(item) for item in observed])
        self.start_container.side_effect = None

        completed = self.attempt()

        self.assertEqual("completed", completed["outcome"], completed)
        self.assertEqual([], self.phases())
        history = completed["evidence"]["failed_attempts"]
        self.assertEqual(
            (self.source_revision, observed),
            (history[0]["source_sha"], history[0]["diagnostics"]),
        )
