
"""Real HTTP/SSE coverage for the one-Project Workbench Codex bridge.

The app-server is an external executable fixture on ``PATH``.  The bridge,
HTTP server, JSON-RPC process boundary and runtime files are real.  No
Workbench business service is mocked here.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
import unittest
from typing import Any

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_CODEX.FEATURE_IWE_CONSOLE_CODEX__tests.bridge_http_support import BridgeHTTPFixture


CODEX_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = CODEX_ROOT.parents[3]
FIXTURE = Path(__file__).with_name("fake_codex.py")
ALLOWED_ORIGIN = "http://127.0.0.1:56317"
MCP_URL = f"{ALLOWED_ORIGIN}/anechoic/mcp"
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


class BridgeHTTPTests(BridgeHTTPFixture):
    def test_event_burst_is_drained_in_order(self) -> None:
        connection, response = self.open_turn("event-burst")
        output: dict[str, list[dict[str, Any]]] = {"events": []}
        reader = self.collect_turn(connection, response, output)
        reader.join(timeout=5)
        self.assertFalse(reader.is_alive())
        packets = [item["event"] for item in output["events"] if item.get("type") == "event"]
        messages = [packet["params"]["sequence"] for packet in packets
                    if packet.get("method") == "item/burst"]
        self.assertEqual(list(range(100)), messages)
        self.assertEqual("turn/completed", packets[-1]["method"])
        self.assertEqual("finished", output["events"][-1]["type"])

    def test_persistent_thread_streams_native_ids_and_interactions(self) -> None:
        status, first = self.json_request("GET", "/conversation")
        self.assertEqual(200, status)
        self.assertEqual("native-thread-1", first["thread_id"])
        self.assertIsInstance(first["thread"], dict)
        self.assertEqual([], first["pending_requests"])

        status, resumed = self.json_request("GET", "/conversation")
        self.assertEqual(200, status)
        self.assertEqual(first["thread_id"], resumed["thread_id"])

        self._assert_message_turn()
        self._assert_approval_turn()
        self._assert_user_input_turn()
        self._assert_elicitation_turn()
        self._assert_interrupted_turn()
        self._assert_final_conversation()

    def _assert_message_turn(self) -> None:
        connection, response = self.open_turn("hello")
        output: dict[str, list[dict[str, Any]]] = {"events": []}
        reader = self.collect_turn(connection, response, output)
        reader.join(timeout=5)
        self.assertFalse(reader.is_alive())
        events = output["events"]
        started = next(item for item in events if item.get("type") == "started")
        streamed = next(
            item for item in events
            if item.get("type") == "event" and item.get("event", {}).get("method") == "item/agentMessage"
        )
        completed_native = next(
            item for item in events
            if item.get("type") == "event" and item.get("event", {}).get("method") == "turn/completed"
        )["event"]
        finished = next(item for item in events if item.get("type") == "finished")
        self.assertEqual("native-thread-1", started["thread_id"])
        self.assertEqual(started["turn_id"], streamed["turn_id"])
        self.assertEqual("item/agentMessage", streamed["event"]["method"])
        self.assertEqual("native-thread-1", completed_native["params"]["threadId"])
        self.assertEqual("completed", finished["status"])

    def _assert_approval_turn(self) -> None:
        connection, response = self.open_turn("approval")
        approval_output: dict[str, list[dict[str, Any]]] = {"events": []}
        approval_reader = self.collect_turn(connection, response, approval_output)
        self.wait_for_pending("native-approval-request")
        status, _ = self.json_request(
            "POST", "/respond", {"id": "native-approval-request", "result": {"approved": True}}
        )
        self.assertEqual(200, status)
        approval_reader.join(timeout=5)
        self.assertFalse(approval_reader.is_alive())
        approval_event = next(
            item for item in approval_output["events"]
            if item.get("type") == "event"
            and item.get("event", {}).get("method") == "item/commandExecution/requestApproval"
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
            next(item for item in approval_output["events"] if item.get("type") == "finished")["status"],
        )

    def _assert_user_input_turn(self) -> None:
        connection, response = self.open_turn("user-input")
        input_output: dict[str, list[dict[str, Any]]] = {"events": []}
        input_reader = self.collect_turn(connection, response, input_output)
        self.wait_for_pending("native-user-input-request")
        status, _ = self.json_request(
            "POST",
            "/respond",
            {"id": "native-user-input-request", "result": {"answer": "yes"}},
        )
        self.assertEqual(200, status)
        input_reader.join(timeout=5)
        self.assertFalse(input_reader.is_alive())
        input_event = next(
            item for item in input_output["events"]
            if item.get("type") == "event"
            and item.get("event", {}).get("method") == "item/tool/requestUserInput"
        )["event"]
        self.assertEqual(
            {"threadId", "turnId", "itemId", "questions"},
            set(input_event["params"]),
        )
        self.assertEqual(
            {"id", "header", "question", "options"},
            set(input_event["params"]["questions"][0]),
        )
        self.assertEqual(
            "item/tool/requestUserInput",
            input_event["method"],
        )
        self.assertEqual(
            "completed",
            next(item for item in input_output["events"] if item.get("type") == "finished")["status"],
        )

    def _assert_elicitation_turn(self) -> None:
        connection, response = self.open_turn("elicitation")
        elicitation_output: dict[str, list[dict[str, Any]]] = {"events": []}
        elicitation_reader = self.collect_turn(connection, response, elicitation_output)
        self.wait_for_pending("native-elicitation-request")
        status, _ = self.json_request(
            "POST",
            "/respond",
            {
                "id": "native-elicitation-request",
                "result": {"action": "accept", "content": {"value": "yes"}},
            },
        )
        self.assertEqual(200, status)
        elicitation_reader.join(timeout=5)
        self.assertFalse(elicitation_reader.is_alive())
        elicitation_event = next(
            item for item in elicitation_output["events"]
            if item.get("type") == "event"
            and item.get("event", {}).get("method") == "mcpServer/elicitation/request"
        )["event"]
        self.assertEqual("mcpServer/elicitation/request", elicitation_event["method"])
        self.assertEqual(
            "completed",
            next(item for item in elicitation_output["events"] if item.get("type") == "finished")["status"],
        )

    def _assert_interrupted_turn(self) -> None:
        connection, response = self.open_turn("interrupt")
        interrupt_output: dict[str, list[dict[str, Any]]] = {"events": []}
        interrupt_reader = self.collect_turn(connection, response, interrupt_output)
        deadline = time.monotonic() + 5
        turn_id = None
        while time.monotonic() < deadline and turn_id is None:
            _, conversation = self.json_request("GET", "/conversation")
            turn_id = conversation.get("active_turn_id")
            if turn_id is None:
                time.sleep(0.05)
        self.assertIsInstance(turn_id, str)
        status, _ = self.json_request("POST", "/interrupt", {"turn_id": "not-the-active-turn"})
        self.assertEqual(400, status)
        status, _ = self.json_request("POST", "/interrupt", {"turn_id": turn_id})
        self.assertEqual(200, status)
        interrupt_reader.join(timeout=5)
        self.assertFalse(interrupt_reader.is_alive())
        self.assertEqual(
            "interrupted",
            next(item for item in interrupt_output["events"] if item.get("type") == "finished")["status"],
        )

    def _assert_final_conversation(self) -> None:
        status, final = self.json_request("GET", "/conversation")
        self.assertEqual(200, status)
        self.assertEqual("native-thread-1", final["thread_id"])
        self.assertIsNone(final["active_turn_id"])
        self.assertEqual([], final["pending_requests"])
        self.assertGreaterEqual(len(final["thread"].get("turns", [])), 1)

    def test_origin_guard_health_route_and_runtime_state(self) -> None:
        status, _ = self.json_request("GET", "/conversation")
        self.assertEqual(200, status)
        status, _, _ = self.request("GET", "/conversation", origin="http://attacker.invalid")
        self.assertEqual(403, status)
        status, health = self.json_request("GET", "/health", origin=None)
        self.assertEqual(200, status)
        self.assertTrue(health.get("ready"))

        state = json.loads(
            (self.root / ".anechoic_runtime/iwe_console/codex/thread.json").read_text(encoding="utf-8")
        )
        self.assertEqual({"thread_id"}, set(state))
        self.assertEqual("native-thread-1", state["thread_id"])

        audit = [json.loads(line) for line in self.audit.read_text(encoding="utf-8").splitlines()]
        argv = next(item["argv"] for item in audit if "argv" in item)
        self.assertEqual("app-server", argv[-1])
        self.assertIn("-c", argv)
        self.assertTrue(any(item.startswith("mcp_servers.anechoic.url=") for item in argv))
        forbidden_flags = ("--model", "--tool", "--tools", "--auth", "--sandbox", "--approval")
        self.assertFalse(any(item == flag or item.startswith(flag + "=") for item in argv for flag in forbidden_flags))
        thread_starts = [
            item for item in audit
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


if __name__ == "__main__":
    unittest.main()
