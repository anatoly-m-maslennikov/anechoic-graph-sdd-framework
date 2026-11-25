"""Project attribution in bounded native Tool observations."""

import unittest

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HealthObservations  # noqa: E402


class HealthIdentityTests(unittest.TestCase):
    def test_project_identity_comes_from_gateway_context(self):
        observations = HealthObservations()
        observations.record(
            "query_run", {},
            {"outcome": "completed", "project_prefix": "FORGED", "project_instance_id": "b" * 64},
            project_prefix="TEST", project_instance_id="a" * 64,
        )
        snapshot = observations.snapshot()
        self.assertEqual({"started_at", "calls"}, set(snapshot))
        row = snapshot["calls"][0]
        self.assertEqual("TEST", row["project_prefix"])
        self.assertEqual("a" * 64, row["project_instance_id"])
        self.assertEqual("completed", row["outcome"])

    def test_invalid_project_identity_is_omitted(self):
        observations = HealthObservations()
        observations.record(
            "query_run", {}, {"outcome": "completed"},
            project_prefix="../private/project", project_instance_id="invalid",
        )
        row = observations.snapshot()["calls"][0]
        self.assertNotIn("project_prefix", row)
        self.assertNotIn("project_instance_id", row)


if __name__ == "__main__":
    unittest.main()
