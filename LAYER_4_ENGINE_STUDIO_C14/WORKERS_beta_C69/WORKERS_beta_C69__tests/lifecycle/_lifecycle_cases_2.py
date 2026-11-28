from . import test_lifecycle_worker as _origin


class LifecycleCases2:
    def _update_runner(self, binding, body):
        def update(ref, version, change=body):
            response = _origin.invoke(
                binding,
                "atom_lifecycle_direct_update",
                {
                    "target": {"ref_id": ref, "version": version},
                    "changes": {"body": change},
                },
            )
            self.assertEqual(0, response.returncode, response.stderr)
            value = _origin.json.loads(response.stdout)
            self.assertIsNone(value["projection_error"], value)
            return value["lifecycle"]

        return update

    def _assert_updated_assets(
        self, update, root, typed, untyped, typed_header, untyped_header, body
    ):
        for ref, version, path, header in (
            ("AN-T-101", 2, typed, typed_header),
            ("AN-T-102@1-draft", 1, untyped, untyped_header),
        ):
            with self.subTest(ref=ref):
                result = update(ref, version)
                self.assertEqual("completed", result["outcome"], result)
                self.assertEqual(
                    (ref, version, path.relative_to(root).as_posix()),
                    (
                        result["artifact"]["ref_id"],
                        result["artifact"]["version"],
                        result["artifact"]["path"],
                    ),
                )
                self.assertEqual((header + body).encode(), path.read_bytes())

    def _assert_asset_bytes(
        self,
        update,
        task,
        typed,
        untyped,
        task_header,
        typed_header,
        untyped_header,
        before,
        body,
    ):
        stale = update("AN-T-101", 1)
        self.assertEqual("source_changed", stale["errors"][0]["code"], stale)
        self.assertEqual([], stale["effects"])
        self.assertEqual((task_header + before).encode(), task.read_bytes())
        self.assertEqual((typed_header + body).encode(), typed.read_bytes())
        self.assertEqual(
            (untyped_header + body).encode(), untyped.read_bytes()
        )

    def _assert_asset_refusals(self, update, body):
        for ref, version, field in (
            ("AN-T-100", 1, "target"),
            ("ZZ-T-101", 2, "target"),
            ("AN-T-101", 2, "summary"),
        ):
            with self.subTest(ref=ref, field=field):
                change = (
                    body.replace("Canary.", "Changed summary.")
                    if field == "summary"
                    else body
                )
                result = update(ref, version, change)
                self.assertEqual("needs_input", result["outcome"], result)
                self.assertIn(field, result["requested_input"])
                self.assertEqual([], result["effects"])

    def test_ticket_asset_direct_update(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-", dir="/tmp"
        ) as directory:
            binding, _, _ = _origin.generation_fixture(directory)
            (
                root,
                task,
                typed,
                untyped,
                task_header,
                typed_header,
                untyped_header,
                before,
                body,
            ) = _origin.ticket_asset_fixture(binding)

            update = self._update_runner(binding, body)

            self._assert_updated_assets(
                update,
                root,
                typed,
                untyped,
                typed_header,
                untyped_header,
                body,
            )

            self._assert_asset_refusals(update, body)
            self._assert_asset_bytes(
                update,
                task,
                typed,
                untyped,
                task_header,
                typed_header,
                untyped_header,
                before,
                body,
            )

    def test_indexed_worker_uses_only_published_carrier(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-indexed-", dir="/tmp"
        ) as directory:
            binding, _, manifest = _origin.generation_fixture(directory)
            manifest.unlink()
            indexed = {
                "max_number": "100",
                "manifest_ref": "AN-S-1@1",
                "component_ids": ["C00"],
                "ticket_labels": ["Task"],
                "endpoints": {
                    "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                    "CONTAINS": [{}, True],
                },
            }
            result = _origin.invoke(
                binding,
                "atom_lifecycle_create_draft",
                {
                    "newAtom": {
                        "template": "task",
                        "container": {"component": "C00"},
                        "body": "## Summary\n\nCanary.\n",
                    }
                },
                structure_sha256="admitted",
                indexed_task=indexed,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            response = _origin.json.loads(result.stdout)
            self.assertIsNone(response["projection_error"], response)
            created = response["lifecycle"]["savedDraft"]
            self.assertEqual("AN-T-101@1-draft", created["ref_id"])
            self.assertEqual(
                [created["path"]], list(response["delta"]["carrier_hashes"])
            )
