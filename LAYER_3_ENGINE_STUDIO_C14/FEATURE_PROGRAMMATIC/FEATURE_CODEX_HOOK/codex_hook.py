
"""Attach the native Codex session and its folder to a ANECHOIC MCP call."""

from __future__ import annotations

import json
from os.path import isabs
import sys
from typing import Any

MAX_EVENT_BYTES = 32 * 1024 * 1024


def deny(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def pre_tool_use(event: object) -> dict[str, Any]:
    if not isinstance(event, dict):
        return deny("ANECHOIC hook event must be an object")
    tool_name = event.get("tool_name")
    if not isinstance(tool_name, str):
        return deny("ANECHOIC hook event requires a tool name")
    if not tool_name.startswith("mcp__anechoic__"):
        return {}
    arguments = event.get("tool_input")
    session_id = event.get("session_id")
    if not isinstance(arguments, dict):
        return deny("ANECHOIC tool arguments must be an object")
    cwd = event.get("cwd")
    if not isinstance(cwd, str) or not isabs(cwd) or "\x00" in cwd:
        return deny("ANECHOIC hook event requires an absolute Codex session folder")
    if arguments.get("project_root", cwd) != cwd:
        return deny("ANECHOIC Project root differs from the Codex session folder")
    if not isinstance(session_id, str) or not session_id.strip():
        return deny("ANECHOIC hook event requires a session ID")
    context = arguments.get("caller_context", {})
    if not isinstance(context, dict):
        return deny("ANECHOIC caller context must be an object")
    if "session_id" in context and context["session_id"] != session_id:
        return deny("ANECHOIC caller session differs from the Codex session")
    updated = dict(arguments)
    updated["project_root"] = cwd
    updated["caller_context"] = {**context, "session_id": session_id}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": updated,
        }
    }


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_EVENT_BYTES + 1)
        if len(raw) > MAX_EVENT_BYTES:
            raise ValueError("ANECHOIC hook input exceeds its size limit")
        event = json.loads(raw)
        result = pre_tool_use(event)
        output = json.dumps(result)
    except ValueError, UnicodeError, RecursionError:
        output = json.dumps(deny("ANECHOIC hook input is invalid or exceeds its size limit"))
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
