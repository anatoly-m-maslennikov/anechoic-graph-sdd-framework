import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68.generation import parse_worker_result
module = importlib.import_module("ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared")


class OrchestratorTicketTests(unittest.TestCase):
    def test_ticket_delta_requires_every_event_to_be_a_bounded_ticket_file_mutation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "_anechoic_fixture"
        control.mkdir()
        binding = {"root": str(root), "control_root": control.name, "project_prefix": "AN"}
        old = control / "__TICKETS" / "AN-T-1--original.md"
        new = control / "001_TICKETS" / "AN-T-1--next.md"

        def event(path, destination=None, kind="modified", directory=False):
            return {"old_path": str(path), "new_path": str(destination) if destination is not None else None,
                    "event_type": kind, "is_directory": directory}

        classify = module.ticket_delta_paths
        expected = sorted([old.relative_to(root).as_posix(), new.relative_to(root).as_posix()])
        self.assertEqual(expected, classify(binding, [event(old, new, "moved"), event(new)]))
        for other in ({}, event(root / "AN-T-5--external.md"), event(old, directory=True),
                      event(old, kind="moved"), event(old, new), event(old.with_suffix(".py")),
                      event(control / "__TKT" / "README.md"), event(control / "AN-T-5--other.md")):
            with self.subTest(event=other):
                self.assertIsNone(classify(binding, [event(old), other]))
        paths = [event(old.with_name(f"AN-T-{index}--task.md")) for index in range(1025)]
        self.assertEqual(500, len(classify(binding, paths[:500])))
        self.assertEqual(1024, len(classify(binding, paths[:1024])))
        self.assertIsNone(classify(binding, paths))
        link = control / "__TKT" / "AN-T-2--symbolic.md"
        link.parent.mkdir()
        link.symlink_to(new)
        self.assertIsNone(classify(binding, [event(link)]))

    def test_worker_delta_must_echo_the_base_and_both_path_parts(self):
        path = "_anechoic_fixture/__TKT/AN-T-1--task.md"
        reuse = {"base_generation": "old"}
        result = {"base_generation": "old", "paths": [["_anechoic_fixture/__TKT", "AN-T-1--task.md"]],
                  "snapshot": {}, "snapshot_sha256": "ignored"}
        self.assertEqual(result, parse_worker_result(json.dumps(result), reuse, [path]))
        for invalid in (result | {"base_generation": "new"}, result | {"paths": [path]}):
            with self.assertRaises(ValueError):
                parse_worker_result(json.dumps(invalid), reuse, [path])
        with self.assertRaises(ValueError):
            parse_worker_result(json.dumps(result), reuse, None)


if __name__ == "__main__":
    unittest.main()
