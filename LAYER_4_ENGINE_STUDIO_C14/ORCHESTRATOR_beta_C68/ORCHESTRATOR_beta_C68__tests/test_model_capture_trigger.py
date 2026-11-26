from types import SimpleNamespace
import unittest

from ..lifecycle_queries import requires_project_capture


class ModelCaptureTriggerTests(unittest.TestCase):
    def test_relocated_model_and_draft_activation(self):
        job = SimpleNamespace(name="atom_lifecycle_change_status", arguments={"target": {"ref_id": "AN-S-1"}})
        carrier = {"id": "AN-S-1", "status": "active", "source_path":
                   "control/ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_DES/a.md"}
        context = {"carriers": [carrier]}
        self.assertTrue(requires_project_capture(job, context, "control"))
        carrier.update(status="draft", source_path="control/ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_SPEC/01_draft/a.md")
        self.assertFalse(requires_project_capture(job, context, "control"))
        job.arguments["targetStatus"] = "active"
        self.assertTrue(requires_project_capture(job, context, "control"))
        carrier["source_path"] = "elsewhere/CONTINUANT_PITCHFORK_C9/a.md"
        self.assertFalse(requires_project_capture(job, context, "control"))
