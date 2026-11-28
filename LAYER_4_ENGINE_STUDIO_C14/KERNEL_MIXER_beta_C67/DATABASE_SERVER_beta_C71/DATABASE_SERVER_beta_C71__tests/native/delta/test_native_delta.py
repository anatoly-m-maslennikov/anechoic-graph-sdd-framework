"""Apply bounded native Ticket deltas without rebuilding the property graph."""

from hashlib import sha256
import json
import unittest


from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _query,
)
from ..atoms.test_native_atoms import _digest, _native_generation


def base_generation():
    data = _native_generation()
    model = json.loads(data["model"])
    model["bindings"]["endpoints"]["CONTAINED_BY"] = [
        {"inverse_alias": "CONTAINS"},
        False,
    ]
    data["model"] = json.dumps(model)
    data["receipt"]["model_descriptor_sha256"] = sha256(
        data["model"].encode()
    ).hexdigest()
    data["snapshot"]["relations"].append(
        {
            "source_kind": "Component",
            "source_ref": "C00",
            "target_kind": "Atom",
            "target_ref": "AN-T-1",
            "relation_type": "CONTAINS",
            "derived": True,
        }
    )
    data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
    return data


def delta(base, paths, atoms, relations):
    snapshot = {
        "schema_version": 2,
        "manifest_sha256": PIN,
        "atoms": atoms,
        "relations": relations,
        "relation_types": ["CONTAINED_BY", "CONTAINS"],
    }
    return BINDING | {
        "base_generation": base,
        "paths": paths,
        "snapshot": snapshot,
        "snapshot_sha256": _digest({"paths": paths, "snapshot": snapshot}),
    }


def edges(reference, target="C00"):
    return [
        {
            "source_kind": "Atom",
            "source_ref": reference,
            "target_kind": "Component",
            "target_ref": target,
            "relation_type": "CONTAINED_BY",
            "derived": False,
        },
        {
            "source_kind": "Component",
            "source_ref": target,
            "target_kind": "Atom",
            "target_ref": reference,
            "relation_type": "CONTAINS",
            "derived": True,
        },
    ]


from ._native_delta_cases_1 import DeltaCases1  # noqa: E402
from ._native_delta_cases_2 import DeltaCases2  # noqa: E402
from ._native_delta_cases_3 import DeltaCases3  # noqa: E402


class NativeDeltaTest(
    DeltaCases1, DeltaCases2, DeltaCases3, unittest.TestCase
):
    def send(self, client, payload):
        response = client.put("/generation/native-delta", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def assert_graph(self, client, expected):
        result = _query(
            client,
            (
                "FROM GRAPH_TABLE (anechoic MATCH (s:Refere"
                "nce)-[e:CONTAINED_BY]->(t:Reference) COLUM"
                "NS (s.ref AS source)) ORDER BY source"
            ),
        )
        self.assertEqual(200, result.status_code, result.text)
        self.assertEqual(
            [[value] for value in expected], result.json()["result"]["rows"]
        )
