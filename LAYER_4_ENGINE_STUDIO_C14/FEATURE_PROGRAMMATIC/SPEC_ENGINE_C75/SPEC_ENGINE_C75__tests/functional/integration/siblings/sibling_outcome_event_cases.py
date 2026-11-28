"""Event selection cases for sibling outcome checks."""


class SiblingOutcomeEventCases:
    def test_outcome_check_accepts_http_client(self):
        path = self.root / self.caller[0]["path"]
        path.write_text(
            path.read_text().replace(
                "'interface': 'render'",
                "'interface': 'render', 'transport': 'http', "
                "'routes': ['POST /render']",
            )
        )
        result = self.check()
        self.assertEqual(
            {"matched"},
            {row["status"] for row in result["directions"].values()},
        )

    def test_selected_event_must_use_requested_interface(self):
        path = self.root / self.caller[2]["path"]
        path.write_text(
            path.read_text().replace(
                "'interface': 'render'", "'interface': 'unrelated'"
            )
        )
        with self.assertRaisesRegex(
            ValueError, "selected event does not use interface render"
        ):
            self.check()

    def test_missing_event_interface_is_rejected(self):
        path = self.root / self.caller[2]["path"]
        path.write_text(
            path.read_text().replace(", 'interface': 'render'", "")
        )
        with self.assertRaisesRegex(
            ValueError, "selected event does not use interface render"
        ):
            self.check()

    def test_output_event_without_interface_is_rejected(self):
        path = self.root / self.caller[2]["path"]
        workflow = path.read_text().replace(
            "'target': 'done'", "'target': 'rendered'"
        )
        path.write_text(
            workflow.replace(
                "'done': {'type': 'final'}",
                "'rendered': {'on': {'return': {'target': 'done', 'guard': {"
                "'type': 'matchesTrace', 'params': {'kind': 'output', "
                "'outcome': 'succeeded'}}}}}, 'done': {'type': 'final'}",
            )
        )
        with self.assertRaisesRegex(
            ValueError, "selected event does not use interface render"
        ):
            self.check(event="return")

    def test_provider_must_offer_requested_interface(self):
        with self.assertRaisesRegex(
            ValueError, "C2 does not declare server unrelated"
        ):
            self.check("unrelated")

    def test_outcome_must_belong_to_selected_provider_interface(self):
        provider = self.root / self.provider[0]["path"]
        provider.write_text(
            provider.read_text().replace(
                "'server': {'render':", "'server': {'unrelated': {}, 'render':"
            )
        )
        caller = self.root / self.caller[2]["path"]
        caller.write_text(
            caller.read_text().replace(
                "'interface': 'render'", "'interface': 'unrelated'"
            )
        )
        result = self.check("unrelated")
        self.assertEqual(
            "unresolved", result["directions"]["caller_manifest"]["status"]
        )
        self.assertNotEqual("matched", result["status"])
