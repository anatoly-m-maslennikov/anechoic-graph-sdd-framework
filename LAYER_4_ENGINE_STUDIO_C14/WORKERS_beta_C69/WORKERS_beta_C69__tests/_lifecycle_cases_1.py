from . import test_lifecycle_worker as _origin


class LifecycleCases1:
    def _epic_runner(self, binding):
        def run(name, arguments):
            result = _origin.invoke(binding, name, arguments)
            self.assertEqual(0, result.returncode, result.stderr)
            response = _origin.json.loads(result.stdout)
            self.assertIsNone(response["projection_error"], response)
            value = response["lifecycle"]
            self.assertEqual("completed", value["outcome"], value)
            return value

        return run

    def _create_epic(self, run):
        created = run(
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "epic",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nEpic canary.\n",
                }
            },
        )
        draft = created["savedDraft"]
        self.assertTrue(created["effects"])
        run(
            "atom_lifecycle_promote_draft",
            {
                "target": {"ref_id": draft["ref_id"], "version": 1},
                "targetStatus": "backlog",
            },
        )
        return draft

    def test_epic_and_create_draft_revision(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-", dir="/tmp"
        ) as directory:
            binding, _, _ = _origin.generation_fixture(directory)

            run = self._epic_runner(binding)

            draft = self._create_epic(run)
            revised = run(
                "atom_lifecycle_create_draft",
                {
                    "sourceCurrent": {
                        "ref_id": draft["atom_id"],
                        "version": 1,
                    },
                    "changes": {
                        "body": "## Summary\n\nEpic canary.\n\nRevised.\n"
                    },
                },
            )
            revision = revised["savedDraft"]
            self.assertEqual(2, revision["version"])
            promoted = run(
                "atom_lifecycle_promote_draft",
                {
                    "target": {"ref_id": revision["ref_id"], "version": 2},
                    "targetStatus": "backlog",
                },
            )
            self.assertEqual(2, promoted["artifact"]["version"])
            self.assertTrue(
                any(
                    "@1-" in effect["target"] for effect in promoted["effects"]
                )
            )

    def _status_runner(self, binding):
        def run(name, arguments):
            result = _origin.invoke(binding, name, arguments)
            self.assertEqual(0, result.returncode, result.stderr)
            response = _origin.json.loads(result.stdout)
            self.assertIsNone(response["projection_error"], response)
            return response["lifecycle"]

        return run

    def _install_status_definitions(self, binding):
        control = _origin.Path(binding["root"]) / binding["control_root"]
        _origin.copy_lifecycle_definitions(control)
        source = (
            _origin.ENGINE.parent / "_anechoic_anechoic/ONTOLOGY_SCORE_C82/"
            "OCCURRENT_METRONOME_C58/_DOM/MTD"
        )
        installed = control / "LAYER_2_META_METHODOLOGY_C58/_DOM/MTD"
        installed.mkdir(parents=True)
        for atom in ("AN-S-1928", "AN-S-1834", "AN-S-1831"):
            (original,) = source.rglob(f"{atom}-MTD-*.md")
            _origin.shutil.copy2(original, installed / original.name)
        return installed

    def _assert_status_rejection(self, run, target, installed):
        rejected = run(
            "atom_lifecycle_change_status",
            {"target": target, "targetStatus": "nonsense"},
        )
        self.assertEqual("needs_input", rejected["outcome"])
        self.assertEqual([], rejected["effects"])
        installed = next(installed.glob("AN-S-1831-*.md"))
        installed.write_bytes(installed.read_bytes() + b"changed\n")
        blocked = run(
            "atom_lifecycle_change_status",
            {"target": target, "targetStatus": "done"},
        )
        self.assertEqual("blocked", blocked["outcome"], blocked)
        self.assertEqual(
            "definition_revalidation_required",
            blocked["errors"][0]["code"],
        )
        self.assertEqual([], blocked["effects"])

    def test_ticket_status_checks_installed_definitions(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-", dir="/tmp"
        ) as directory:
            binding, _, _ = _origin.generation_fixture(directory)
            installed = self._install_status_definitions(binding)

            run = self._status_runner(binding)

            created = run(
                "atom_lifecycle_create_draft",
                {
                    "newAtom": {
                        "template": "task",
                        "container": {"component": "C00"},
                        "body": "## Summary\n\nStatus canary.\n",
                    }
                },
            )
            self.assertEqual("completed", created["outcome"], created)
            draft = created["savedDraft"]
            target = {"ref_id": draft["ref_id"], "version": 1}
            self.assertEqual(
                "completed",
                run(
                    "atom_lifecycle_promote_draft",
                    {"target": target, "targetStatus": "backlog"},
                )["outcome"],
            )
            target["ref_id"] = draft["atom_id"]
            changed = run(
                "atom_lifecycle_change_status",
                {"target": target, "targetStatus": "in_queue"},
            )
            self.assertEqual("completed", changed["outcome"], changed)
            self.assertEqual("in_queue", changed["artifact"]["status"])
            self.assertTrue(changed["effects"])
            self._assert_status_rejection(run, target, installed)

    def _archive_runners(self, binding):
        def run(name, arguments):
            result = _origin.invoke(binding, name, arguments)
            self.assertEqual(0, result.returncode, result.stderr)
            response = _origin.json.loads(result.stdout)
            self.assertIsNone(response["projection_error"], response)
            return response["lifecycle"]

        def create(summary):
            draft = run(
                "atom_lifecycle_create_draft",
                {
                    "newAtom": {
                        "template": "task",
                        "container": {"component": "C00"},
                        "body": f"## Summary\n\n{summary}\n",
                    }
                },
            )["savedDraft"]
            promoted = run(
                "atom_lifecycle_promote_draft",
                {
                    "target": {"ref_id": draft["ref_id"], "version": 1},
                    "targetStatus": "backlog",
                },
            )
            self.assertEqual("completed", promoted["outcome"], promoted)
            return promoted["artifact"]

        return run, create

    def test_archive_requires_current_replacement(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-", dir="/tmp"
        ) as directory:
            binding, _, _ = _origin.generation_fixture(directory)
            control = _origin.Path(binding["root"]) / binding["control_root"]
            _origin.copy_lifecycle_definitions(control)

            run, create = self._archive_runners(binding)

            original = create("Original")
            target = {"ref_id": original["atom_id"], "version": 1}
            refused = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("needs_input", refused["outcome"], refused)
            self.assertEqual([], refused["effects"])
            replacement = create("Replacement")
            path = _origin.Path(binding["root"]) / replacement["path"]
            data = path.read_text()
            self.assertNotIn("\nrelations:", data)
            path.write_text(
                data.replace(
                    "\n---\n",
                    "\nrelations:\n  IS_REPLACEMENT_FOR: ["
                    + original["atom_id"]
                    + "]\n---\n",
                    1,
                )
            )
            original_path = _origin.Path(binding["root"]) / original["path"]
            container = original_path.with_suffix("")
            container.mkdir()
            refused = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("needs_input", refused["outcome"], refused)
            self.assertEqual([], refused["effects"])
            container.rmdir()
            archived = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("completed", archived["outcome"], archived)
            self.assertEqual("archived", archived["artifact"]["status"])
            self.assertTrue(archived["effects"])
            self.assertFalse(
                (_origin.Path(binding["root"]) / original["path"]).exists()
            )
