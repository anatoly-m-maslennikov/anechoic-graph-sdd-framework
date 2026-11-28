from . import test_incremental_startup as source


class IncrementalCases0:
    def test_incremental_capture_uses_admitted_status_domains(self):
        self.reuse["status_domains"] = {
            "S": ["active", "draft", "archived"],
            "T": ["active", "draft", "archived", "reviewed"],
            "P": ["active", "draft", "archived"],
            "C": ["active", "draft", "archived"],
        }
        (self.live / "AN-T-3-task.md").write_text(
            source.carrier(3, "reviewed")
        )
        (self.live / "AN-T-4-task.md").write_text(source.carrier(4, "unknown"))
        result = self.capture()
        row = next(
            row
            for row in result["snapshot"]["atoms"]
            if row["reference"] == "AN-T-3"
        )
        self.assertEqual(
            ("reviewed", "Current"), (row["status"], row["status_group"])
        )
        self.assertTrue(
            any(
                issue["relative_path"].endswith("AN-T-4-task.md")
                for issue in result["snapshot"]["ingestion_issues"]
            )
        )

    def _replay_inputs(self):
        base = {
            "binding": {},
            "reuse": None,
            "replay_graph": True,
            "watcher_guarded": True,
            "foreground": True,
        }
        replay = "Graph replay requires a watcher-guarded foreground capture"
        fields = "Invalid managed Worker fields"
        option = "Invalid managed Worker option"
        invalid = (
            ({"watcher_guarded": False}, replay),
            ({"foreground": False}, replay),
            ({"paths": []}, replay),
            ({"archive": {}}, replay),
            ({"unexpected": True}, replay),
            ({"archive": None, "paths": None}, replay),
            (
                {"replay_graph": False, "paths": None, "structure": None},
                fields,
            ),
            ({"replay_graph": False, "unexpected": True}, fields),
            *(
                ({flag: 1, "unexpected": True}, option)
                for flag in (
                    "watcher_guarded",
                    "foreground",
                    "incremental",
                    "replay_graph",
                    "defer_graph",
                    "graph_only",
                )
            ),
        )
        return base, invalid

    def test_watcher_replay_requires_managed_foreground_without_explicit_paths(
        self,
    ):
        base, invalid = self._replay_inputs()
        for options, message in invalid:
            with self.subTest(options=options):
                response = source.command_with_fixture(
                    source.WORKER,
                    base | options,
                    "--generation-dir",
                    "/fixture",
                )
                self.assertEqual(1, response.returncode)
                (issue,) = source.json.loads(response.stdout)[
                    "ingestion_failure"
                ]["issues"]
                self.assertEqual(message, issue["message"])

    def test_deferred_warm_start_ignores_graph_input_changes(self):
        self.reuse["graph_config"] = {"include": []}
        self.reuse["inputs"]["graph"] = "old-graph-signature"
        (self.root / "changed.py").write_text("value = 1\n")
        request = {
            "binding": self.binding,
            "reuse": self.reuse,
            "watcher_guarded": True,
            "incremental": True,
            "foreground": True,
            "defer_graph": True,
        }
        signature = (
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61."
            "import_graph__shared.graph_input_signature"
        )
        with (
            source.patch(
                signature, side_effect=AssertionError("graph scanned")
            ),
            source.patch.dict(
                source.os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}
            ),
            source.TemporaryDirectory(dir=self.tmp.name) as output,
        ):
            response = source.command_with_fixture(
                source.WORKER,
                request,
                "--generation-dir",
                str(source.Path(output).resolve()),
            )
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual(
            {"base_generation": "a" * 64, "unchanged": True},
            source.json.loads(response.stdout),
        )
        self.assertIn('"mode":"reused","phase":"model_ready"', response.stderr)
        self.assertIn(
            '"mode":"reused","phase":"structure_ready"', response.stderr
        )
        self.assertNotIn("realization_graph_ready", response.stderr)

    def _events_factory(self):
        def events(response):
            prefix = "ANECHOIC_STARTUP_TIMING "
            return [
                source.json.loads(line[len(prefix) :])
                for line in response.stderr.splitlines()
                if line.startswith(prefix)
            ]

        return events

    def _assert_warm_timing(self, warm, events):
        by_phase = {event["phase"]: event for event in events(warm)}
        self.assertEqual("reused", by_phase["model_ready"]["mode"])
        self.assertEqual("reused", by_phase["structure_ready"]["mode"])
        self.assertEqual(
            "disabled", by_phase["realization_graph_ready"]["mode"]
        )
        self.assertEqual(
            0, by_phase["non_archived_load_started"]["changed_paths"]
        )
        self.assertGreaterEqual(
            by_phase["non_archived_load_started"]["comparison_ns"], 0
        )
        self.assertGreaterEqual(
            by_phase["non_archived_load_started"]["checkpoint_validation_ns"],
            0,
        )

    def test_timing_reports_compilation_and_checkpoint_reuse(self):
        events = self._events_factory()

        with source.patch.dict(
            source.os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}
        ):
            with source.TemporaryDirectory(dir=self.tmp.name) as output:
                cold = source.command_with_fixture(
                    source.WORKER,
                    {
                        "binding": self.binding,
                        "reuse": None,
                        "foreground": True,
                        "defer_graph": True,
                    },
                    "--generation-dir",
                    str(source.Path(output).resolve()),
                )
            self.assertEqual(0, cold.returncode, cold.stderr)
            modes = {
                event["phase"]: event.get("mode") for event in events(cold)
            }
            self.assertEqual("built", modes["model_ready"])
            self.assertEqual("built", modes["structure_ready"])
            self.assertEqual("disabled", modes["realization_graph_ready"])
            self.assertIn("non_archived_load_started", modes)
            request = {
                "binding": self.binding,
                "reuse": self.reuse,
                "watcher_guarded": True,
                "incremental": True,
                "foreground": True,
            }
            with source.TemporaryDirectory(dir=self.tmp.name) as output:
                warm = source.command_with_fixture(
                    source.WORKER,
                    request,
                    "--generation-dir",
                    str(source.Path(output).resolve()),
                )
            self.assertEqual(0, warm.returncode, warm.stderr)
            self.assertTrue(source.json.loads(warm.stdout)["unchanged"])
            self._assert_warm_timing(warm, events)

    def test_rejected_checkpoint_does_not_report_reuse(self):
        self.reuse["folder_hashes"] = {}
        request = {
            "binding": self.binding,
            "reuse": self.reuse,
            "watcher_guarded": True,
            "incremental": True,
            "foreground": True,
        }
        with (
            source.patch.dict(
                source.os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}
            ),
            source.TemporaryDirectory(dir=self.tmp.name) as output,
        ):
            response = source.command_with_fixture(
                source.WORKER,
                request,
                "--generation-dir",
                str(source.Path(output).resolve()),
            )
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertIn("receipt", source.json.loads(response.stdout))
        prefix = "ANECHOIC_STARTUP_TIMING "
        events = [
            source.json.loads(line[len(prefix) :])
            for line in response.stderr.splitlines()
            if line.startswith(prefix)
        ]
        milestones = [
            event
            for event in events
            if event["phase"]
            in {"model_ready", "structure_ready", "realization_graph_ready"}
        ]
        self.assertTrue(milestones)
        self.assertNotIn("reused", [event.get("mode") for event in milestones])
