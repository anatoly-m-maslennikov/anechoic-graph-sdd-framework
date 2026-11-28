"""Assertions for the bridge HTTP protocol fixture."""

from typing import Any

FORBIDDEN_OVERRIDE_KEYS = {
    "model",
    "modelProvider",
    "model_provider",
    "toolConfig",
    "tool_config",
    "allowedTools",
    "allowed_tools",
    "mcpServers",
    "mcp_servers",
    "approvalPolicy",
    "approval_policy",
    "sandbox",
    "auth",
    "credentials",
}


class BridgeProtocolCases:
    def _assert_approval_turn(self) -> None:
        connection, response = self.open_turn("approval")
        approval_output: dict[str, list[dict[str, Any]]] = {"events": []}
        approval_reader = self.collect_turn(
            connection, response, approval_output
        )
        self.wait_for_pending("native-approval-request")
        status, _ = self.json_request(
            "POST",
            "/respond",
            {"id": "native-approval-request", "result": {"approved": True}},
        )
        self.assertEqual(200, status)
        approval_reader.join(timeout=5)
        self.assertFalse(approval_reader.is_alive())
        approval_event = next(
            item
            for item in approval_output["events"]
            if item.get("type") == "event"
            and item.get("event", {}).get("method")
            == "item/commandExecution/requestApproval"
        )["event"]
        self.assertEqual(
            {"threadId", "turnId", "itemId", "reason"},
            set(approval_event["params"]),
        )
        self.assertEqual(
            "item/commandExecution/requestApproval",
            approval_event["method"],
        )
        self.assertEqual(
            "completed",
            next(
                item
                for item in approval_output["events"]
                if item.get("type") == "finished"
            )["status"],
        )

    def _assert_launch_audit(self, audit):
        argv = next(item["argv"] for item in audit if "argv" in item)
        self.assertEqual("app-server", argv[-1])
        self.assertIn("-c", argv)
        self.assertTrue(
            any(item.startswith("mcp_servers.anechoic.url=") for item in argv)
        )
        forbidden_flags = (
            "--model",
            "--tool",
            "--tools",
            "--auth",
            "--sandbox",
            "--approval",
        )
        self.assertFalse(
            any(
                item == flag or item.startswith(flag + "=")
                for item in argv
                for flag in forbidden_flags
            )
        )
        thread_starts = [
            item
            for item in audit
            if item.get("in", {}).get("method") == "thread/start"
        ]
        self.assertEqual(1, len(thread_starts))
        for packet in audit:
            incoming = packet.get("in")
            if not isinstance(incoming, dict):
                continue
            params = incoming.get("params")
            if isinstance(params, dict):
                self.assertFalse(FORBIDDEN_OVERRIDE_KEYS & set(params))
