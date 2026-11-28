from . import test_incremental_startup as source


class IncrementalCases2:
    def test_archive_delta_excludes_wrong_status_and_keeps_valid_rows(self):
        invalid = self.archive / "AN-T-9-task.md"
        valid = self.archive / "AN-T-10@1-task.md"
        invalid.write_text(source.carrier(9))
        valid.write_text(source.carrier(10, "archived"))
        result = self.capture(archive_roots=self.roots)
        snapshot = result["snapshot"]
        self.assertEqual(
            [(valid.name, "Archived")],
            [
                (row["filename"], row["status_group"])
                for row in snapshot["atoms"]
            ],
        )
        relative = invalid.relative_to(self.root).as_posix()
        self.assertEqual(
            [relative],
            [issue["relative_path"] for issue in snapshot["ingestion_issues"]],
        )
        self.assertEqual(
            source.sha256(invalid.read_bytes()).hexdigest(),
            result["carrier_hashes"][relative],
        )

    def test_legacy_delta_falls_back_and_malformed_carrier_is_reported(self):
        live = self.live / "AN-T-1-task.md"
        live.write_text(
            "---\nidentity: {atom_id: AN-T-1}\ncontext: {container: "
            "{component: C00}}\n"
            "state: {status: active, version: 1}\n---\n\n## "
            "Summary\n\nLegacy.\n"
        )
        hashes = self.checkpoint_hashes()
        self.reuse.update(
            carrier_hashes=hashes,
            folder_hashes=source.checkpoint_folders(hashes),
        )
        live.write_text(live.read_text().replace("Legacy.", "Changed."))
        self.assertIn("receipt", self.capture())
        live.write_text("---\ninvalid: [\n---\n")
        result = self.capture()
        relative = live.relative_to(self.root).as_posix()
        self.assertEqual([], result["snapshot"]["atoms"])
        self.assertEqual(
            [relative],
            [
                issue["relative_path"]
                for issue in result["snapshot"]["ingestion_issues"]
            ],
        )
        self.assertEqual(
            source.sha256(live.read_bytes()).hexdigest(),
            result["carrier_hashes"][relative],
        )

    def test_schema_and_large_diff_require_reconciliation(self):
        schema = self.reuse["inputs"].pop("carrier_schema")
        self.assertIn("receipt", self.capture())
        self.assertEqual(
            {"incompatible": True}, self.capture(archive_roots=self.roots)
        )
        self.reuse["inputs"]["carrier_schema"] = schema
        many = {
            f"{self.binding['control_root']}/__TICKETS/AN-T-{i}-task.md": "c"
            * 64
            for i in range(2000, 3025)
        }
        with source.patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "ADAPTERS_C30__shared.native_carrier_hashes",
            return_value=many,
        ):
            self.assertIn("receipt", self.capture())
            self.assertEqual(
                {"incompatible": True}, self.capture(archive_roots=self.roots)
            )

    def test_folder_hashes_are_canonical_and_validate_paths(self):
        (self.live / "AN-T-4--состояние.md").write_text(source.carrier(4))
        values = self.checkpoint_hashes()
        self.reuse["folder_hashes"] = source.checkpoint_folders(values)
        self.reuse["carrier_hashes"] = dict(reversed(list(values.items())))
        self.assertEqual(
            {"base_generation": "a" * 64, "unchanged": True}, self.capture()
        )
        self.reuse["carrier_hashes"] = values | {"../escape.md": "c" * 64}
        self.reuse["folder_hashes"] = source.checkpoint_folders(
            self.reuse["carrier_hashes"]
        )
        self.assertIn("receipt", self.capture())
        self.assertEqual(
            {"incompatible": True}, self.capture(archive_roots=self.roots)
        )

    def test_current_inventory_rejects_literal_backslash(self):
        (self.live / "AN-T-4-invalid\\name.md").write_text(source.carrier(4))
        request = {
            "binding": self.binding,
            "reuse": self.reuse,
            "watcher_guarded": True,
            "incremental": True,
            "foreground": True,
        }
        with source.TemporaryDirectory(dir=self.tmp.name) as output:
            response = source.command_with_fixture(
                source.WORKER, request, "--generation-dir", output
            )
            self.assertEqual(1, response.returncode, response.stderr)
            (issue,) = source.json.loads(response.stdout)["ingestion_failure"][
                "issues"
            ]
            self.assertEqual(
                "Invalid carrier checkpoint path", issue["message"]
            )
            self.assertFalse(any(source.Path(output).iterdir()))
