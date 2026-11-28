"""Additional startup checkpoint tests."""

from . import test_startup_checkpoint as source
from .startup_checkpoint_archive_cases import StartupCheckpointArchiveCases


class StartupCheckpointCases(StartupCheckpointArchiveCases):
    def test_disk_checkpoint_updates_changed_folders_and_archive_against_latest_base(
        self,
    ):
        directory = self.enterContext(source.TemporaryDirectory(dir="/tmp"))
        database = source.Path(directory).resolve() / "projection.duckdb"
        data = source._baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        with source._server(database) as client:
            first = self._accepted(client, "/generation", data)
        with source._server_without_lifespan(database) as client:
            proof, moved, initial_folders = self.assert_moved_checkpoint(
                client, first, snapshot, current, archived
            )
        self._assert_disk_checkpoint(
            database,
            data["carrier_hashes"],
            initial_folders,
            {
                source._path(current): None,
                source._path(moved): "d" * 64,
                source._path(archived): None,
            },
        )
        with source._server(database) as client:
            self.assertEqual(proof, self._reuse(client))
        self._assert_disk_checkpoint(
            database, proof["carrier_hashes"], proof["folder_hashes"], {}
        )

    def assert_moved_checkpoint(
        self, client, first, snapshot, current, archived
    ):
        proof = self._reuse(client)
        cwd, history = current["relative_path"], archived["relative_path"]
        folder = source._folder(archived["filename"], "b" * 64)
        initial_folders = {
            cwd: source._folder(current["filename"], "a" * 64),
            history: folder,
        }
        self.assertEqual(initial_folders, proof["folder_hashes"])
        moved = current | {
            "relative_path": f"{cwd}/new",
            "summary": "edited",
        }
        paths = [
            [row["relative_path"], row["filename"]] for row in (current, moved)
        ]
        delta = source._delta(
            first,
            snapshot,
            paths,
            [moved],
            {source._path(moved): "d" * 64},
        )
        current_base = self._accepted(
            client,
            "/generation/native-delta",
            delta | {"archive_pending": True},
        )
        proof = self.assert_pending_move(client, moved, history, folder)
        proof = self.assert_archive_delete(
            client,
            first,
            snapshot,
            history,
            archived,
            current_base,
            paths,
            proof,
            moved,
        )
        return proof, moved, initial_folders

    def assert_pending_move(self, client, moved, history, folder):
        proof = self._reuse(client)
        self.assertTrue(proof["archive_pending"])
        self.assertEqual(
            {
                moved["relative_path"]: source._folder(
                    moved["filename"], "d" * 64
                ),
                history: folder,
            },
            proof["folder_hashes"],
        )
        return proof

    def test_latest_live_digest_is_retained_across_offline_reversion(self):
        directory = source.Path(
            self.enterContext(source.TemporaryDirectory(dir="/tmp"))
        ).resolve()
        database = directory / "projection.duckdb"
        data = source._baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        path = source._path(current)
        carrier = directory / "carrier.md"
        carrier.write_bytes(b"original")
        original = source.sha256(carrier.read_bytes()).hexdigest()
        data["carrier_hashes"][path] = original
        with source._server_without_lifespan(database) as client:
            base = self._accepted(client, "/generation", data)
            paths = [[current["relative_path"], current["filename"]]]
            for content in (b"first edit", b"latest admitted bytes"):
                carrier.write_bytes(content)
                updated = source.sha256(carrier.read_bytes()).hexdigest()
                delta = source._delta(
                    base, snapshot, paths, [current], {path: updated}
                )
                base = self._accepted(
                    client, "/generation/native-delta", delta
                )
        self.assert_reverted_digest(
            database,
            data,
            current,
            archived,
            path,
            carrier,
            original,
            updated,
            base,
        )

    def assert_reverted_digest(
        self,
        database,
        data,
        current,
        archived,
        path,
        carrier,
        original,
        updated,
        base,
    ):
        carrier.write_bytes(b"original")
        initial_folders = {
            current["relative_path"]: source._folder(
                current["filename"], original
            ),
            archived["relative_path"]: source._folder(
                archived["filename"], "b" * 64
            ),
        }
        self._assert_disk_checkpoint(
            database, data["carrier_hashes"], initial_folders, {path: updated}
        )
        with source._server(database) as client:
            proof = self._reuse(client)
            self.assertEqual(base, proof["base_generation"])
            self.assertEqual(updated, proof["carrier_hashes"][path])
            self.assertNotEqual(
                source.sha256(carrier.read_bytes()).hexdigest(),
                proof["carrier_hashes"][path],
            )
            self.assertEqual(
                source._folder(current["filename"], updated),
                proof["folder_hashes"][current["relative_path"]],
            )
        self._assert_disk_checkpoint(
            database, proof["carrier_hashes"], proof["folder_hashes"], {}
        )

    def test_live_checkpoint_skips_folder_rebuild_and_changes_roll_back(self):
        data = source._baseline()
        current, _ = data["snapshot"]["atoms"]
        path = source._path(current)
        paths = [[current["relative_path"], current["filename"]]]
        with source.duckdb.connect() as connection:
            source.carrier_checkpoint.update_checkpoint(connection, data)
            delta = source._delta(
                "base", data["snapshot"], paths, [current], {path: "c" * 64}
            )
            with source.patch.object(
                source.carrier_checkpoint, "_folder_hashes"
            ) as folder_hashes:
                connection.begin()
                source.carrier_checkpoint.update_checkpoint(
                    connection, delta, delta=True
                )
                connection.commit()
                connection.begin()
                source.carrier_checkpoint.update_checkpoint(
                    connection,
                    delta | {"carrier_hashes": {path: "d" * 64}},
                    delta=True,
                )
                connection.rollback()
                folder_hashes.assert_not_called()
            self.assertEqual(
                data["carrier_hashes"] | {path: "c" * 64},
                source.carrier_checkpoint.read_checkpoint(connection),
            )
            self.assert_checkpoint_rollback(connection, data, path)

    def assert_checkpoint_rollback(self, connection, data, path):
        connection.begin()
        source.carrier_checkpoint.fold_checkpoint(connection)
        connection.rollback()
        self.assertEqual(
            [(path, "c" * 64)],
            connection.execute(
                "SELECT * FROM ops_generation_carrier_changes"
            ).fetchall(),
        )
        self.assertEqual(
            data["carrier_hashes"],
            dict(
                connection.execute(
                    "SELECT path, digest FROM ops_generation_carrier_digests"
                ).fetchall()
            ),
        )

    def test_conditional_archive_reuse_and_replacement_preserve_off_path_archives(
        self,
    ):
        data = source._baseline()
        snapshot = data["snapshot"]
        current, archived = snapshot["atoms"]
        off_path = archived | {
            "relative_path": current["relative_path"],
            "reference": "AN-T-1@3",
            "exact_ref": "AN-T-1@3",
            "version": 3,
            "filename": "AN-T-1@3-extra.md",
        }
        snapshot["atoms"].append(off_path)
        data["carrier_hashes"][source._path(off_path)] = "d" * 64
        data["receipt"]["snapshot_sha256"] = source._digest(snapshot)
        with source._server() as client:
            base = self._accepted(client, "/generation", data)
            pending = source.BINDING | {
                "base_generation": base,
                "archive_pending": True,
            }
            stale = client.put(
                "/generation/reuse",
                json=pending | {"base_generation": "stale"},
            )
            self.assertEqual(409, stale.status_code, stale.text)
            self._accepted(client, "/generation/reuse", pending)
            self.assertTrue(self._reuse(client)["archive_pending"])
            complete = source.BINDING | {
                "base_generation": base,
                "unchanged": True,
            }
            self.assertEqual(
                base, self._accepted(client, "/generation/archive", complete)
            )
            self.assertNotIn("archive_pending", self._reuse(client))
            self._accepted(client, "/generation/reuse", pending)
            self.assert_archive_replacement(
                client, base, snapshot, current, off_path
            )

    def assert_archive_replacement(
        self, client, base, snapshot, current, off_path
    ):
        empty = snapshot | {"atoms": [], "relations": []}
        replacement = source.BINDING | {
            "base_generation": base,
            "snapshot": empty,
            "snapshot_sha256": source._digest(empty),
            "carrier_hashes": {},
            "replace": True,
        }
        self._accepted(client, "/generation/archive", replacement)
        proof = self._reuse(client)
        self.assertNotIn("archive_pending", proof)
        self.assertEqual(
            {
                source._path(current): "a" * 64,
                source._path(off_path): "d" * 64,
            },
            proof["carrier_hashes"],
        )
        self.assertEqual(
            [[off_path["exact_ref"]]],
            source._query(
                client,
                (
                    "SELECT exact_ref FROM native_references WHERE "
                    "status_group = 'Archived'"
                ),
            ).json()["result"]["rows"],
        )
