"""Verify that a draft is visible through the shared backend."""


async def _assert_lifecycle_projection(test, client, root):
    created = await client.call_tool(
        "atom_lifecycle_create_draft",
        {
            "newAtom": {
                "template": "axiom",
                "container": {"component": "C00"},
                "lens": "SPEC",
                "body": "## Summary\n\nVerify Backend lifecycle.\n",
            }
        },
    )
    payload = created.structured_content
    test.assertEqual("completed", payload["status"], payload)
    draft = payload["savedDraft"]
    test.assertTrue((root / draft["path"]).is_file())
    visible = await client.call_tool(
        "query_run",
        {
            "sql": (
                "SELECT exact_ref FROM native_references "
                "WHERE exact_ref = '" + draft["ref_id"] + "'"
            ),
            "result_delivery": "inline",
        },
    )
    test.assertFalse(visible.is_error, visible.structured_content)
    test.assertEqual([[draft["ref_id"]]], visible.structured_content["rows"])
