"""Check native Atom Header fields in full and delta writes."""

import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import _query, _server
from .test_native_atoms import _digest
from .test_native_delta import base_generation, delta, edges


class NativeHeaderColumnsTest(unittest.TestCase):
    def send(self, client, payload):
        response = client.put("/generation/native-delta", json=payload)
        self.assertEqual(200, response.status_code, response.text)

    def test_atom_header_columns_across_full_and_delta(self):
        data = base_generation()
        atom = data["snapshot"]["atoms"][0]
        atom.update(container_component="C00", tier=2, template="TASK")
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        sql = 'SELECT reference, "header.container.component", "header.tier", "header.context.template" FROM mrt_atoms ORDER BY reference'
        with _server() as client:
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertEqual([["AN-T-1", "C00", 2, "TASK"], ["AN-T-1@1", None, None, None]],
                             _query(client, sql).json()["result"]["rows"])
            atom = atom | {"container_component": None, "tier": None, "template": "UPDATED"}
            path = [atom["relative_path"], atom["filename"]]
            self.send(client, delta(admitted.json()["result"]["generation"], [path], [atom], edges(atom["reference"])))
            self.assertEqual([["AN-T-1", None, None, "UPDATED"], ["AN-T-1@1", None, None, None]],
                             _query(client, sql).json()["result"]["rows"])


