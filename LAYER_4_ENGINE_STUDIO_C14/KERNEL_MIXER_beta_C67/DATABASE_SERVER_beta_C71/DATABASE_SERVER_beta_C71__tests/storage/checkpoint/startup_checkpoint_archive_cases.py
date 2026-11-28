"""Archive assertions for startup checkpoint tests."""

from . import test_startup_checkpoint as source


class StartupCheckpointArchiveCases:
    def assert_archive_delete(
        self,
        client,
        first,
        snapshot,
        history,
        archived,
        current_base,
        paths,
        proof,
        moved,
    ):
        delete = source._delta(
            first, snapshot, [[history, archived["filename"]]], [], {}
        )
        stale = client.put("/generation/archive", json=delete)
        self.assertEqual(409, stale.status_code, stale.text)
        bad = source._delta(current_base, snapshot, [paths[-1]], [], {})
        self.assertEqual(
            400, client.put("/generation/archive", json=bad).status_code
        )
        self.assertEqual(proof, self._reuse(client))
        self._accepted(
            client,
            "/generation/archive",
            delete | {"base_generation": current_base},
        )
        proof = self._reuse(client)
        self.assertNotIn("archive_pending", proof)
        self.assertEqual(
            {source._path(moved): "d" * 64}, proof["carrier_hashes"]
        )
        rows = source._query(
            client, 'SELECT relative_path, "content.summary" FROM atoms'
        ).json()["result"]["rows"]
        self.assertEqual([[moved["relative_path"], "edited"]], rows)
        return proof
