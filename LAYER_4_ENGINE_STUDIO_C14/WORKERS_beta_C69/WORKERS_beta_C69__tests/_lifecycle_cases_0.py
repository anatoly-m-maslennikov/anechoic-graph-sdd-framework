from . import test_lifecycle_worker as _origin


class LifecycleCases0:
    def _admission_base(self):
        binding = {
            "root": "/project",
            "control_root": "control",
            "manifest_path": "manifest",
            "manifest_sha256": "digest",
            "project_prefix": "AN",
        }
        base = {
            "binding": binding,
            "name": "atom_lifecycle_create_draft",
            "arguments": {},
            "base_generation": "generation",
            "structure_sha256": "structure",
        }
        return binding, base

    def _admission_cases(self):
        binding, base = self._admission_base()
        indexed = {
            "max_number": "1",
            "manifest_ref": "AN-S-1",
            "component_ids": [],
            "ticket_labels": [],
            "endpoints": {},
        }
        context = {
            "structure": {},
            "ticket_labels": [],
            "max_numbers": {},
            "carriers": [],
            "lenses": [],
            "model": None,
            "has_descendants": False,
            "endpoints": {},
        }
        cases = (
            (base | {"base_generation": ""}, "Invalid lifecycle request"),
            (
                base | {"binding": {}},
                "manifest_build_CS4__shared failed: Invalid binding fields",
            ),
            (
                base | {"binding": binding | {"root": ""}},
                "manifest_build_CS4__shared failed: Invalid binding "
                "identity or path",
            ),
            (
                base | {"indexed_task": indexed, "binding": {}},
                "Invalid indexed lifecycle request",
            ),
            (
                base | {"indexed_task": indexed | {"component_ids": [1]}},
                "Invalid indexed task request",
            ),
            (
                base | {"lifecycle_context": context | {"has_descendants": 0}},
                "Invalid lifecycle context",
            ),
        )
        return cases

    def test_request_admission_preserves_refusal_messages(self):
        cases = self._admission_cases()
        for request, message in cases:
            with self.subTest(message=message):
                result = _origin.command_with_fixture(
                    "WORKERS_beta_C69.lifecycle_worker", request
                )
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(message, result.stderr.strip())

    def test_warning_bearing_carrier_cannot_satisfy_lifecycle_effect(self):
        adapter = (
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "ADAPTERS_C30__shared"
        )
        for name, capture in (
            ("atom_lifecycle_create_draft", "capture_carrier_delta"),
            ("atom_lifecycle_direct_update", "capture_ticket_delta"),
        ):
            with (
                self.subTest(name=name),
                _origin.tempfile.TemporaryDirectory(
                    prefix="ane-lifecycle-", dir="/tmp"
                ) as directory,
            ):
                binding, _, _ = _origin.generation_fixture(directory)
                arguments = self.warning_arguments(name, binding)
                payload = {
                    "binding": binding,
                    "name": name,
                    "arguments": arguments,
                    "base_generation": "test-generation",
                    "structure_sha256": _origin.structure_digest(binding),
                }
                with _origin.patch(
                    f"{adapter}.{capture}", side_effect=self.warning_delta
                ) as fixture:
                    response = _origin.command_with_fixture(
                        "WORKERS_beta_C69.lifecycle_worker", payload
                    )
                self.assertEqual(0, response.returncode, response.stderr)
                body = _origin.json.loads(response.stdout)
                self.assertEqual(
                    "completed", body["lifecycle"]["outcome"], body
                )
                self.assertTrue(body["lifecycle"]["effects"])
                fixture.assert_called_once()
                self.assertIsNone(body["delta"])
                self.assertEqual(
                    "Lifecycle carrier delta contains invalid Project files",
                    body["projection_error"],
                )

    def test_stale_structure_refuses_before_write(self):
        with _origin.tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-", dir="/tmp"
        ) as directory:
            binding, _, _ = _origin.generation_fixture(directory)
            result = _origin.invoke(
                {**binding, "manifest_sha256": "0" * 64},
                "atom_lifecycle_create_draft",
                {},
            )
            self.assertNotEqual(0, result.returncode)
            result = _origin.invoke(
                binding,
                "atom_lifecycle_create_draft",
                {"newAtom": {"template": "component_contract"}},
            )
            self.assertEqual(0, result.returncode, result.stderr)
            lifecycle = _origin.json.loads(result.stdout)["lifecycle"]
            self.assertEqual("needs_input", lifecycle["outcome"])
            self.assertEqual(
                "Add the Component Contract to the Component Manifest.",
                lifecycle["requested_input"]["newAtom"]["error"],
            )
            self.assertEqual([], lifecycle["effects"])
            response = _origin.invoke(
                binding,
                "atom_lifecycle_create_draft",
                {
                    "newAtom": {
                        "template": "task",
                        "container": {"component": "C00"},
                        "body": "## Summary\n\nCanary.\n",
                    }
                },
                structure_sha256="0" * 64,
            )
            self.assertEqual(0, response.returncode, response.stderr)
            value = _origin.json.loads(response.stdout)
            self.assertEqual("failed", value["lifecycle"]["outcome"], value)
            self.assertEqual([], value["lifecycle"].get("effects", []))
            self.assertIn(
                "admitted Model and Structure inputs",
                value["projection_error"],
            )
            self.assertIsNone(value["delta"])
