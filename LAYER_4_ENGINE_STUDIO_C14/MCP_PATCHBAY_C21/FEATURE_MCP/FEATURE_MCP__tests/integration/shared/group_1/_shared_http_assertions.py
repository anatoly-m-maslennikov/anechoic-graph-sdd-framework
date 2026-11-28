"""Mock backend and receipt assertions for shared HTTP tests."""


def backend_handler(messages, project, tool, json, httpx2):
    def backend(request):
        key = (request.method, request.url.path)
        data = json.loads(request.content) if request.content else None
        messages.append((key, data))
        if key == ("POST", "/") and "project_root" not in data["arguments"]:
            fault = {
                "scope": "project",
                "code": "missing_project_root",
                "message": "missing_project_root",
            }
            return httpx2.Response(200, json={"error": fault, "project": None})
        result = {
            ("GET", "/health"): {"pid": 101, "initialized": True},
            ("GET", "/"): {
                "tools": [tool.model_dump(mode="json", by_alias=True)]
            },
            ("POST", "/selection"): project,
            ("POST", "/"): {"value": {"rows": [[1]]}, "text": None},
        }[key]
        envelope = {"result": result}
        if key == ("POST", "/"):
            envelope["project"] = {
                "prefix": "MA",
                "instance_id": project["instance_id"],
            }
        return httpx2.Response(200, json=envelope)

    return backend


def assert_messages(self, messages, root):
    self.assertEqual(
        [
            (("POST", "/selection"), {"project_root": root}),
            (
                ("POST", "/"),
                {
                    "name": "query_run",
                    "arguments": {"sql": "SELECT 1", "project_root": root},
                    "session_id": None,
                    "public_base_url": None,
                },
            ),
            (
                ("POST", "/"),
                {
                    "name": "query_run",
                    "arguments": {"sql": "SELECT 1"},
                    "session_id": None,
                    "public_base_url": None,
                },
            ),
        ],
        messages[-3:],
    )


async def assert_rejected_receipt(self, client, session, arguments, calls):
    calls.clear()
    web = await client.post("/anechoic/Main/api/run", json=arguments)
    self.assertEqual(502, web.status_code)
    failure = web.json()
    self.assertEqual("project_receipt_mismatch", failure["code"])
    self.assertEqual("failed", failure["tool_result"]["outcome"])
    self.assertNotIn("private", web.text)
    mcp = await session.call_tool("query_run", arguments)
    self.assertTrue(mcp.is_error)
    self.assertEqual(failure["tool_result"], mcp.structured_content)
    self.assertEqual(["/selection", "/", "/selection", "/"], calls)


async def assert_valid_receipt(self, client, session, arguments):
    web = await client.post("/anechoic/Main/api/run", json=arguments)
    mcp = await session.call_tool("query_run", arguments)
    self.assertEqual(200, web.status_code)
    self.assertFalse(mcp.is_error)
    self.assertEqual({"rows": [["private"]]}, web.json())
    self.assertEqual(web.json(), mcp.structured_content)


async def assert_gateway_replies(self, gateway, tool, project, root, types):
    await gateway.initialize()
    self.assertEqual([tool], gateway.tools)
    self.assertEqual(project, await gateway.select_project(root))
    params = types.CallToolRequestParams(
        name="query_run",
        arguments={"sql": "SELECT 1", "project_root": root},
    )
    response = await gateway.call(None, params)
    self.assertEqual({"rows": [[1]]}, response.structured_content)
    refused = await gateway.call(
        None,
        types.CallToolRequestParams(
            name="query_run", arguments={"sql": "SELECT 1"}
        ),
    )
    self.assertTrue(refused.is_error)
    self.assertEqual(
        ["missing_project_root"],
        refused.structured_content["diagnostics"],
    )


def receipt_backend(
    self, calls, arguments, selected, json, httpx2, get_receipt
):
    def backend(request):
        data = json.loads(request.content)
        calls.append(request.url.path)
        if request.url.path == "/selection":
            self.assertEqual(arguments["project_root"], data["project_root"])
            return httpx2.Response(200, json={"result": selected})
        self.assertEqual(
            arguments["project_root"], data["arguments"]["project_root"]
        )
        self.assertEqual(
            selected["instance_id"],
            request.headers["X-Anechoic-Project-Instance"],
        )
        return httpx2.Response(
            200,
            json={
                "project": get_receipt(),
                "result": {"value": {"rows": [["private"]]}, "text": None},
            },
        )

    return backend
