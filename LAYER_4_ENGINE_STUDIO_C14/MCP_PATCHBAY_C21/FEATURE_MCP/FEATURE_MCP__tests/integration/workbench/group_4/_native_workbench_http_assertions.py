"""Workspace HTTP assertions shared by native Workbench tests."""


async def check_workspace_http(self, app, httpx2):
    async with httpx2.AsyncClient(
        transport=httpx2.ASGITransport(app=app),
        base_url="http://127.0.0.1:18093",
    ) as client:
        path = "/anechoic/Anechoic/api"
        status = await client.post(f"{path}/status", json={})
        self.assertEqual(200, status.status_code, status.text)
        self.assertEqual({"mode": "live_index"}, status.json())
        wrong_status_root = await client.post(
            f"{path}/status", json={"project_root": "/wrong/project"}
        )
        self.assertEqual(400, wrong_status_root.status_code)

        async def call(operation, arguments, **envelope):
            return await client.post(
                f"{path}/interface",
                json={
                    "operation": operation,
                    "arguments": arguments,
                    **envelope,
                },
            )

        await check_workspace_operations(self, client, call, path)


async def check_workspace_operations(self, client, call, path):
    opened = await call("workspace_open", {"session_id": "http-session"})
    self.assertEqual(200, opened.status_code, opened.text)
    workspace = opened.json()
    self.assertEqual("Anechoic", workspace["project_name"])
    self.assertIn(
        "/anechoic/iwe-console/Anechoic?workspace=http-session",
        workspace["workspace_url"],
    )
    identity = {
        "workspace_id": workspace["workspace_id"],
        "view_id": workspace["active_view_id"],
    }
    sql = (
        "SELECT exact_ref FROM native_references WHERE exact_ref = "
        "'AN-T-009@2'"
    )
    updated = await call(
        "view_update", identity | {"sql": sql, "expected_revision": 0}
    )
    self.assertEqual(200, updated.status_code, updated.text)
    checked = await call("view_check", identity)
    self.assertTrue(checked.json()["valid"], checked.text)
    result = await call("view_run", identity)
    self.assertEqual("success", result.json()["status"], result.text)
    fetched = await call(
        "view_fetch", identity | {"result_delivery": "inline"}
    )
    self.assertEqual([["AN-T-009@2"]], fetched.json()["rows"])
    saved = await call("view_save", identity)
    self.assertEqual(200, saved.status_code, saved.text)
    saved_url = saved.json()["saved_query_url"]
    self.assertIn("/anechoic/iwe-console/Anechoic?query=", saved_url)
    for url in (
        saved_url,
        saved_url.replace("/iwe-console/", "/workbench/"),
    ):
        loaded = await client.post(f"{path}/load", json={"reference": url})
        self.assertEqual(sql, loaded.json()["sql"], loaded.text)
    listed = await client.post(f"{path}/saved-list", json={})
    self.assertEqual(
        saved.json()["saved_query_id"],
        listed.json()["items"][0]["saved_query_id"],
    )
    await self._check_workspace_refusals(client, call, path, workspace)
