from . import test_incremental_startup as source


class IncrementalCases1:
    def test_foreground_unchanged_and_offline_add_edit_move_delete(self):
        self.assertEqual(
            {"base_generation": "a" * 64, "unchanged": True}, self.capture()
        )
        first = self.live / "AN-T-1-task.md"
        stamp = first.stat()
        first.write_text(first.read_text().replace("Ticket 1.", "Ticket X."))
        source.os.utime(first, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        second = self.live / "AN-T-2-task.md"
        moved = self.live / "AN-T-2-moved.md"
        second.rename(moved)
        added = self.live / "AN-T-3-task.md"
        added.write_text(source.carrier(3))
        result = self.capture()
        paths = {
            str(source.Path(parent) / name) for parent, name in result["paths"]
        }
        self.assertEqual(
            {
                p.relative_to(self.root).as_posix()
                for p in (first, second, moved, added)
            },
            paths,
        )
        self.assertEqual(
            {
                p.relative_to(self.root).as_posix()
                for p in (first, moved, added)
            },
            set(result["carrier_hashes"]),
        )
        self.assertEqual(3, len(result["snapshot"]["atoms"]))

    def _addressed_inputs(self):
        first = self.live / "AN-T-1-task.md"
        second = self.live / "AN-T-2-task.md"
        first.write_text(first.read_text().replace("Ticket 1.", "Ticket X."))
        second.write_text(second.read_text().replace("Ticket 2.", "Ticket Y."))
        relative = first.relative_to(self.root).as_posix()
        deferred_reuse = self.reuse | {
            "graph_config": {},
            "inputs": self.reuse["inputs"] | {"graph": "pending"},
        }
        request = {
            "binding": self.binding,
            "watcher_guarded": True,
            "paths": [relative],
        }
        return first, relative, deferred_reuse, request

    def test_addressed_delta_captures_only_the_named_ticket(self):
        first, relative, deferred_reuse, request = self._addressed_inputs()
        for mode, reuse in (
            ("foreground", self.reuse),
            ("defer_graph", deferred_reuse),
        ):
            with (
                self.subTest(mode=mode),
                source.TemporaryDirectory(dir=self.tmp.name) as output,
            ):
                result = self.run_worker(
                    source.Path(output).resolve(),
                    request | {mode: True, "reuse": reuse},
                )
                self.assertEqual(
                    reuse["base_generation"], result.get("base_generation")
                )
                self.assertEqual(
                    [
                        [
                            first.parent.relative_to(self.root).as_posix(),
                            first.name,
                        ]
                    ],
                    result["paths"],
                )
                self.assertEqual(
                    {relative: source.sha256(first.read_bytes()).hexdigest()},
                    result["carrier_hashes"],
                )
                self.assertEqual(
                    ["AN-T-1"],
                    [row["reference"] for row in result["snapshot"]["atoms"]],
                )
                self.assertEqual([], list(source.Path(output).iterdir()))

    def test_archive_unchanged_move_and_delete(self):
        self.assertEqual(
            {"base_generation": "a" * 64, "unchanged": True},
            self.capture(archive_roots=self.roots),
        )
        original = self.archive / "AN-T-8@1-task.md"
        moved = self.archive / "AN-T-8@1-moved.md"
        original.rename(moved)
        result = self.capture(archive_roots=self.roots)
        self.assertEqual(
            {original.name, moved.name}, {row[1] for row in result["paths"]}
        )
        self.assertEqual(
            ["Archived"],
            [row["status_group"] for row in result["snapshot"]["atoms"]],
        )
        moved.unlink()
        self.assertEqual(
            {}, self.capture(archive_roots=self.roots)["carrier_hashes"]
        )

    def test_full_archive_checks_roots_and_keeps_foreground_out(self):
        archive = {"roots": self.roots, "endpoints": self.reuse["endpoints"]}
        request = {
            "binding": self.binding,
            "reuse": None,
            "watcher_guarded": True,
            "archive": archive,
        }
        with source.TemporaryDirectory(dir=self.tmp.name) as output:
            result = self.run_worker(source.Path(output).resolve(), request)
            self.assertEqual({"snapshot", "carrier_hashes"}, set(result))
            self.assertEqual(
                ["AN-T-8@1"],
                [row["reference"] for row in result["snapshot"]["atoms"]],
            )
            self.assertEqual(
                {f"{self.roots[0]}/AN-T-8@1-task.md"},
                set(result["carrier_hashes"]),
            )
            self.assertEqual([], list(source.Path(output).iterdir()))
            invalid = request | {
                "archive": archive
                | {"roots": [self.live.relative_to(self.root).as_posix()]}
            }
            response = source.command_with_fixture(
                source.WORKER, invalid, "--generation-dir", output
            )
            self.assertEqual(1, response.returncode, response.stderr)
            (issue,) = source.json.loads(response.stdout)["ingestion_failure"][
                "issues"
            ]
            self.assertEqual(
                "Deferred archive directory is outside the selected "
                "native archive trees",
                issue["message"],
            )
            self.assertEqual([], list(source.Path(output).iterdir()))

    def test_incompatible_checkpoint_falls_back(self):
        self.reuse["folder_hashes"] = {}
        self.assertIn("receipt", self.capture())
        self.assertEqual(
            {"incompatible": True}, self.capture(archive_roots=self.roots)
        )
