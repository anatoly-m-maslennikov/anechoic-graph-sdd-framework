"""Exercise historical lifecycle invoke responses without network transport."""

import asyncio
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
CASE = json.loads((HERE / "case.json").read_text())
UNKNOWN = {
    "code": "write_outcome_unknown",
    "message": "The lifecycle write outcome is unknown.",
}


def load(version):
    package = types.ModuleType("_lifecycle_replay")
    package.__path__ = []
    admission = types.ModuleType("_lifecycle_replay.admission")
    admission.failure = lambda code, message: {
        "error": {"code": code, "message": message}
    }
    admission.peer = None
    sys.modules[package.__name__] = package
    sys.modules[admission.__name__] = admission
    module = types.ModuleType("_lifecycle_replay.lifecycle")
    module.__package__ = package.__name__
    sys.modules[module.__name__] = module
    namespace = module.__dict__
    source = (HERE / CASE[version]["fixture"]).read_text()
    exec(compile(source, CASE[version]["fixture"], "exec"), namespace)
    return namespace


async def invoke(module, response):
    async def peer(*args, **kwargs):
        return {"result": response}

    module["peer"] = peer
    return (
        await module["invoke"](
            "atom_lifecycle_archive",
            {"target": {}},
            "orchestrator",
            {},
            "instance",
        )
    )["result"]["value"]


class Replay(unittest.TestCase):
    def test_blocked_and_controls(self):
        blocked = {
            "write_state": "known",
            "projection": {"state": "blocked"},
            "lifecycle": {
                "outcome": "blocked",
                "errors": [{"code": "write_blocked"}],
            },
        }
        inconsistent = [
            {**blocked, "lifecycle": {"outcome": "completed"}},
            {**blocked, "write_state": "unknown"},
        ]
        ready = {
            "write_state": "known",
            "projection": {"state": "ready"},
            "lifecycle": {"outcome": "completed"},
        }
        for version in ("before", "fixed"):
            module = load(version)

            value = asyncio.run(invoke(module, blocked))
            if version == "before":
                self.assertEqual(value["status"], "failed")
                self.assertEqual(value["errors"], [UNKNOWN])
            else:
                self.assertEqual(value["status"], "blocked")
                self.assertEqual(value["errors"], [{"code": "write_blocked"}])
            for response in inconsistent:
                self.assertEqual(
                    asyncio.run(invoke(module, response))["errors"], [UNKNOWN]
                )
            self.assertEqual(
                asyncio.run(invoke(module, ready)), {"status": "completed"}
            )


if __name__ == "__main__":
    unittest.main()
