"""Manifest child delegation validation scenarios."""

from importlib import import_module

check_child_outcome = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88."
    "DELEGATION_VERIFICATION_C89._package__shared"
).check_child_outcome


class ManifestValidationCases:
    def test_exact_pin_action_guarantee_and_public_binding_are_required(self):
        for pin, before, after, expected in (
            (self.solution, "'AN-S-2@1'", "'AN-S-2@2'", "conflicting"),
            (self.solution, ", 'manifest': 'AN-S-2@1'", "", "unresolved"),
            (self.child, "action='render'", "action='inspect'", "unresolved"),
            (self.child, "'limit': 4", "'limit': 6", "conflicting"),
            (
                self.child,
                "interface='renderer'",
                "interface='other'",
                "conflicting",
            ),
        ):
            with self.subTest(before=before, after=after):
                restore = self.mutate(pin, before, after)
                try:
                    self.assertEqual(expected, self.check()["status"])
                finally:
                    restore()
        restore = self.mutate(
            self.solution, "ANSWERS: [AN-S-1@1]", "ANSWERS: [AN-S-1@2]"
        )
        try:
            with self.assertRaisesRegex(ValueError, "missing exact ANSWERS"):
                self.check()
        finally:
            restore()

    def test_child_manifest_declares_identity_and_parent(self):
        with self.assertRaisesRegex(
            ValueError, "manifest does not match source pin"
        ):
            check_child_outcome(
                self.root,
                self.solution,
                "C2",
                {**self.child, "version": 2},
                parent_manifest=self.parent,
                event="render",
                lean=self.lean,
            )
        restore = self.mutate(
            self.child, "component_id='C2'", "component_id='C4'"
        )
        try:
            with self.assertRaisesRegex(
                ValueError, "component does not match"
            ):
                self.check()
        finally:
            restore()
        self.mutate(self.child, "component: C1", "component: C4")
        self.child["container_component"] = "C4"
        with self.assertRaisesRegex(ValueError, "not a declared child"):
            self.check()
