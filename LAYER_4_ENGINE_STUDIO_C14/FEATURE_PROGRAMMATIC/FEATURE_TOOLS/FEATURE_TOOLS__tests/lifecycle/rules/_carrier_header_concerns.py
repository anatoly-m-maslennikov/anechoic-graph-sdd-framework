"""Check Component and Atom concerns in native Headers."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
    native_header_model_fields,
    native_header_view,
)


class _HeaderConcernCases:
    def test_issue_concern_round_trips_affected_components(self):
        issue = self.old | {
            "context": self.old["context"] | {"template": "problem"}
        }
        concern = {"components": ["C21", "C45"]}
        header = canonical_native_header(issue | {"concern": concern})
        locators = [
            {
                "subject": value,
                "path": "Project Structure.components",
                "relation": "affects",
            }
            for value in concern["components"]
        ]
        self.assertEqual(header["concern"], locators)
        self.assertEqual(native_header_view(header)["concern"], locators)
        self.assertEqual(canonical_native_header(header), header)
        self.assertEqual(
            native_header_model_fields(header)["concern"], locators
        )
        self.assertNotIn("components", native_header_model_fields(header))
        for invalid in ([], "C21", ["C21", "C21"], ["MCP"], [21]):
            with (
                self.subTest(components=invalid),
                self.assertRaises(ValueError),
            ):
                canonical_native_header(
                    issue | {"concern": {"components": invalid}}
                )
        with self.assertRaises(ValueError):
            canonical_native_header(
                issue
                | {
                    "concern": {
                        "subject": "Atom",
                        "path": "Model",
                        "relation": "about",
                    }
                }
            )
        with self.assertRaises(ValueError):
            native_header_view(
                header | {"concern": ["component(id=C21);exec(x)"]}
            )

    def test_ticket_concern_validation_and_historical_references(self):
        first = {
            "subject": "C51",
            "path": "Project Structure.components",
            "relation": "affects",
        }
        second = {"subject": "AN-S-1", "path": "Model", "relation": "about"}
        header = canonical_native_header(
            self.old | {"concern": [first, second]}
        )
        self.assertEqual(
            native_header_view(header)["concern"], [first, second]
        )
        for invalid in (
            [],
            [first, first],
            [{"subject": "C51"}],
            [first | {"extra": "x"}],
            [first | {"path": " "}],
        ):
            with self.subTest(concern=invalid), self.assertRaises(ValueError):
                native_header_view(header | {"concern": invalid})
        self._assert_historical_concern(header, first)

    def _assert_historical_concern(self, header, first):
        historical = header | {
            "concern": ["component(id=C51)", "atom(id=AN-S-1)"]
        }
        self.assertEqual(
            native_header_view(historical)["concern"], historical["concern"]
        )
        with self.assertRaisesRegex(ValueError, "cannot be converted"):
            canonical_native_header(historical)
        self.assertEqual(
            canonical_native_header(
                header | {"concern": ["component(id=C51)"]}
            )["concern"],
            [first],
        )
        grouped = {
            key: value
            for key, value in header.items()
            if key not in {"container", "priority"}
        }
        grouped |= {
            "structure": {
                "container": header["container"],
                "priority": header["priority"],
            },
            "concern": {"components": ["C51"]},
        }
        self.assertEqual(
            native_header_view(grouped)["concern"], {"components": ["C51"]}
        )
        self.assertEqual(canonical_native_header(grouped)["concern"], [first])

    def test_component_concern_is_ticket_only(self):
        locator = {"subject": "Atom", "path": "Model", "relation": "about"}
        for atom_id, context in (
            ("AN-S-1", {"container": {"component": "C9"}, "tier": 1}),
            (
                "AN-P-1",
                {"container": {"component": "C9"}, "template": "manifest"},
            ),
        ):
            source = self.old | {
                "identity": {"atom_id": atom_id},
                "context": context,
            }
            header = canonical_native_header(source | {"concern": locator})
            self.assertEqual(native_header_view(header)["concern"], locator)
            for concern in (
                {"components": ["C9"]},
                locator | {"components": ["C9"]},
            ):
                with self.subTest(atom_id=atom_id, concern=concern):
                    with self.assertRaisesRegex(ValueError, "Concern"):
                        native_header_view(header | {"concern": concern})
                    with self.assertRaisesRegex(ValueError, "Concern"):
                        canonical_native_header(source | {"concern": concern})
            with self.assertRaisesRegex(ValueError, "Concern"):
                canonical_native_header(
                    source | {"concern": locator | {"unknown": "value"}}
                )
            archived = header | {
                "concern": {"components": ["C9"]},
                "state": header["state"] | {"status": "archived"},
            }
            self.assertEqual(
                native_header_view(archived)["concern"], {"components": ["C9"]}
            )
            with self.assertRaisesRegex(ValueError, "Concern"):
                canonical_native_header(archived)
