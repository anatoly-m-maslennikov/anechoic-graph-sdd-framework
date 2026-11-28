from __future__ import annotations

import asyncio
from pathlib import Path
import unittest
from unittest.mock import Mock

from ..group_3 import _workbench_mcp_fixture as mcp_fixture
from ....native_query_test_support import WorkbenchTools
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    QueryExecutionError,
    WorkbenchUnavailableError,
)

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    CHECK,
    LOAD,
    NATIVE_TOOLS,
    PAGE,
    QUERY_LOG_LIST,
    RUN,
    SAVED_LIST,
    SAVE_VIEW,
    SCHEMA,
    VIEW_CREATE,
    VIEW_DUPLICATE,
    WORKSPACE_OPEN,
    native_tools,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.\
    RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    ExplicitBlockingRuntimeFailure,
)


MCP_ROOT = Path(__file__).resolve().parents[4]


class FakeService(mcp_fixture.FakeServiceBase):
    _fixture_globals = globals()


class WorkbenchToolsTests(unittest.TestCase):
    async def _exercise_calls(self, owner):
        await mcp_fixture.exercise_initial(self, owner, globals())
        await mcp_fixture.exercise_remaining(self, owner, globals())

    def _assert_fake_calls(self, fake):
        self.assertEqual(
            self._expected_calls_first() + self._expected_calls_last(),
            fake.calls,
        )

    @staticmethod
    def _expected_calls_first():
        return [
            (
                RUN,
                "SELECT 1",
                100,
                None,
                False,
                None,
                None,
                "file",
                "json_matrix",
            ),
            (PAGE, "q-1", 0, 1, None, "file", "json_matrix"),
            (CHECK, "SELECT 1", None),
            (
                RUN,
                "SELECT 2",
                100,
                2,
                True,
                None,
                "saved",
                "file",
                "json_matrix",
            ),
            (SAVE_VIEW, "SELECT 3", "view"),
            (
                RUN,
                "SELECT 4",
                100,
                None,
                True,
                None,
                "   ",
                "file",
                "json_matrix",
            ),
        ]

    @staticmethod
    def _expected_calls_last():
        return [
            (LOAD, "q_2"),
            (SCHEMA,),
            (SAVED_LIST, 3),
            (WORKSPACE_OPEN, {"session_id": "session-1"}),
            (VIEW_CREATE, {"workspace_id": "session-1"}),
            (
                VIEW_DUPLICATE,
                {"workspace_id": "session-1", "view_id": "source-view"},
            ),
            (QUERY_LOG_LIST, {}),
        ]

    def test_native_descriptors_and_one_owner_handle_all_calls_and_close(self):
        self.assertEqual(
            list(NATIVE_TOOLS), [tool.name for tool in native_tools()]
        )
        tools = {tool.name: tool for tool in native_tools()}
        self.assertNotIn("query_save", tools)
        self.assertIsNone(tools[WORKSPACE_OPEN].meta)
        self.assertIsNone(tools[VIEW_CREATE].meta)
        self.assertEqual(
            {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "minLength": 1},
                    "view_id": {"type": "string", "minLength": 1},
                },
                "required": ["workspace_id", "view_id"],
                "additionalProperties": False,
            },
            tools[VIEW_DUPLICATE].input_schema,
        )
        self.assertFalse(tools[VIEW_DUPLICATE].annotations.read_only_hint)
        self.assertFalse(tools[RUN].annotations.read_only_hint)
        self.assertTrue(tools[CHECK].annotations.read_only_hint)
        self.assertTrue(tools[SCHEMA].annotations.read_only_hint)
        fake = FakeService()
        owner = WorkbenchTools(query_owner=fake)

        asyncio.run(self._exercise_calls(owner))
        self._assert_fake_calls(fake)
        self.assertTrue(fake.closed)

    def test_invalid_arguments_are_not_sent_to_the_service(self):
        owner = WorkbenchTools(query_owner=FakeService())
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(RUN, {"sql": 1}))
        self.assertEqual("query_error", caught.exception.code)
        self.assertEqual("sql must be a string", caught.exception.message)
        self.assertEqual([], owner._query_owner.calls)

    @staticmethod
    def _invalid_arguments():
        return (
            WorkbenchToolsTests._invalid_page_arguments()
            + WorkbenchToolsTests._invalid_other_arguments()
        )

    @staticmethod
    def _invalid_page_arguments():
        return (
            (
                PAGE,
                {"query_id": "q", "offset": True},
                "offset must be a non-negative integer",
            ),
            (
                PAGE,
                {"query_id": "q", "offset": -1},
                "offset must be a non-negative integer",
            ),
            (
                PAGE,
                {"query_id": "q", "offset": 0, "page_size": True},
                "page_size must be an integer",
            ),
            (
                PAGE,
                {"query_id": "q", "offset": 0, "unknown": 1},
                (
                    "Expected query_id and optional pagination, grid and result "
                    "options"
                ),
            ),
        )

    @staticmethod
    def _invalid_other_arguments():
        return (
            (
                RUN,
                {"sql": "SELECT 1", "page_size": True},
                "page_size must be an integer",
            ),
            (
                RUN,
                {"sql": "SELECT 1", "name": "forbidden"},
                "name is only valid when save is true",
            ),
            (
                RUN,
                {"sql": "SELECT 1", "save": "yes"},
                "save must be a boolean",
            ),
            (
                RUN,
                {"sql": "SELECT 1", "preview": -1},
                "preview must be a non-negative integer",
            ),
            (
                CHECK,
                {"sql": "SELECT 1", "name": "forbidden"},
                "Expected only cursor_position and sql",
            ),
            (
                SAVE_VIEW,
                {"sql": "SELECT 1", "name": 1},
                "name must be a string",
            ),
            ("query_unknown", {"sql": "SELECT 1"}, "Unknown Workbench tool"),
        )

    def test_arguments_and_tool_name_are_strict(self):
        owner = WorkbenchTools(query_owner=FakeService())
        for name, arguments, message in self._invalid_arguments():
            with (
                self.subTest(name=name, arguments=arguments),
                self.assertRaises(ExplicitBlockingRuntimeFailure) as caught,
            ):
                asyncio.run(owner.call(name, arguments))
            self.assertEqual("query_error", caught.exception.code)
            self.assertEqual(message, caught.exception.message)
        self.assertEqual([], owner._query_owner.calls)

    def _assert_unexpected_failures(self, owner):
        owner._query_owner.run.side_effect = RuntimeError(
            "unexpected connector fault"
        )
        with self.assertRaisesRegex(
            RuntimeError, "unexpected connector fault"
        ):
            asyncio.run(owner.call(RUN, {"sql": "SELECT 1"}))

        owner._query_owner.run.side_effect = RuntimeError(
            "unexpected connector fault: restart required"
        )
        with self.assertRaisesRegex(
            RuntimeError, "unexpected connector fault"
        ):
            asyncio.run(owner.call(RUN, {"sql": "SELECT 1"}))

        owner._query_owner.page = Mock(
            side_effect=ValueError("unknown query_id")
        )
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(PAGE, {"query_id": "expired", "offset": 0}))
        self.assertEqual("query_error", caught.exception.code)

    def test_known_query_and_unavailable_failures_are_explicit_but_unexpected_failure_is_not(
        self,
    ):
        owner = WorkbenchTools(
            query_owner=Mock(
                run=Mock(
                    side_effect=QueryExecutionError(
                        "query failed: Parser Error"
                    )
                )
            )
        )
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(RUN, {"sql": "SELECT FROM"}))
        self.assertEqual("query_error", caught.exception.code)
        self.assertEqual(
            "query failed: Parser Error", caught.exception.message
        )

        owner._query_owner.run.side_effect = QueryExecutionError(
            "query failed: missing column 'restart required'"
        )
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(RUN, {"sql": 'SELECT "restart required"'}))
        self.assertEqual("query_error", caught.exception.code)

        owner._query_owner.run.side_effect = ValueError(
            "query result delivery failed: unsupported value"
        )
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(RUN, {"sql": "SELECT unsupported"}))
        self.assertEqual("query_error", caught.exception.code)
        self.assertEqual(
            "query result delivery failed: unsupported value",
            caught.exception.message,
        )

        owner._query_owner.run.side_effect = WorkbenchUnavailableError(
            "query store unavailable; Workbench restart required"
        )
        with self.assertRaises(ExplicitBlockingRuntimeFailure) as caught:
            asyncio.run(owner.call(RUN, {"sql": "SELECT 1"}))
        self.assertEqual("workbench_unavailable", caught.exception.code)
        self.assertEqual(
            "Workbench unavailable; restart required", caught.exception.message
        )

        self._assert_unexpected_failures(owner)


if __name__ == "__main__":
    unittest.main()
