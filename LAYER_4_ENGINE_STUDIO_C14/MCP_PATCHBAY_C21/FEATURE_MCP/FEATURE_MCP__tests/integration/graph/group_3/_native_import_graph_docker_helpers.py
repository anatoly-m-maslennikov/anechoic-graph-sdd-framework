"""Helpers for native import-graph image test cases."""


def launch_archive(root, name, control, g):
    container = (
        g["subprocess"]
        .check_output(
            [
                "docker",
                "run",
                "--detach",
                "--pull=never",
                "--init",
                "--name",
                name,
                "--label",
                "anechoic.test=import-graph-canary",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,size=256m",
                "--pids-limit",
                "128",
                "--cpus",
                "1",
                "--publish",
                "127.0.0.1::8092",
                "--volume",
                f"{root}:/project:rw",
                "--env",
                "ANECHOIC_RUNTIME_NAMESPACE=docker",
                "--env",
                f"ANECHOIC_CONTROL_ROOT={control}",
                "--env",
                g["docker_deadline_env"](),
                g["os"].environ["ANECHOIC_IMAGE"],
                "mcp-http",
            ],
            text=True,
            timeout=g["image_timeout"](60),
        )
        .strip()
    )
    return container


def wait_archive(project, container, g):
    deadline = g["monotonic"]() + 90
    while g["observing"](container, deadline):
        try:
            if g["request"](project.url + g["HEALTH_PATH"]) == (
                200,
                {"state": "ready"},
            ):
                break
        except OSError:
            pass
        g["sleep"](0.2)
    else:
        logs = g["subprocess"].run(
            ["docker", "logs", "--tail", "12", container],
            capture_output=True,
            text=True,
        )
        raise RuntimeError(
            f"Archive Project failed to start: {logs.stdout}{logs.stderr}"
        )


async def create(call, summary):
    created = await call(
        "atom_lifecycle_create_draft",
        {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": f"## Summary\n\n{summary}\n",
            }
        },
    )
    draft = created["savedDraft"]
    promoted = await call(
        "atom_lifecycle_promote_draft",
        {
            "target": {
                "ref_id": draft["ref_id"],
                "version": draft["version"],
            },
            "targetStatus": "backlog",
        },
    )
    return promoted["artifact"]


async def assert_ticket_promotion(self, call):
    created = await call(
        "atom_lifecycle_create_draft",
        {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": "## Summary\n\nPromotion canary.\n",
            }
        },
    )
    draft = created["savedDraft"]
    atom = draft["atom_id"]
    sql = (
        'SELECT reference, "header.state.version", "header.state.status" FROM atoms '
        f"WHERE reference = '{atom}' OR reference LIKE '{atom}@%' "
        'ORDER BY "header.state.version", reference'
    )
    await call(
        "atom_lifecycle_promote_draft",
        {
            "target": {
                "ref_id": draft["ref_id"],
                "version": draft["version"],
            },
            "targetStatus": "backlog",
        },
    )
    await assert_ticket_revision(self, call, draft, atom, sql)


async def assert_ticket_revision(self, call, draft, atom, sql):
    revised = await call(
        "atom_lifecycle_update",
        {
            "sourceCurrent": {"ref_id": draft["atom_id"], "version": 1},
            "changes": {
                "body": "## Summary\n\nPromotion canary.\n\nRevised.\n"
            },
        },
        status="draft_created",
    )
    revision = revised["savedDraft"]
    await call(
        "atom_lifecycle_promote_draft",
        {
            "target": {
                "ref_id": revision["ref_id"],
                "version": revision["version"],
            },
            "targetStatus": "backlog",
        },
    )
    self.assertEqual(
        [[atom + "@1", 1, "archived"], [atom, 2, "backlog"]],
        self._rows(sql),
    )


async def assert_archive_refused(self, project, call, monotonic):
    original = await create(call, "Archive original canary.")
    atom = original["atom_id"]
    arguments = {"target": {"ref_id": atom, "version": original["version"]}}
    sql = (
        f'SELECT reference, "header.state.status" FROM atoms '
        f"WHERE reference IN ('{atom}', '{atom}@{original['version']}')"
    )
    started = monotonic()
    refused = await call("atom_lifecycle_archive", arguments, status="failed")
    print(
        f"archive refusal: {monotonic() - started:.3f}s",
        flush=True,
    )
    self.assertEqual("invalid_input", refused["errors"][0]["code"], refused)
    self.assertEqual([], refused["effects"])
    self.assertEqual([[atom, "backlog"]], project._rows(sql))
    return original, atom, arguments, sql


async def assert_archive_replacement(
    self, project, call, original, atom, arguments, sql, asyncio
):
    replacement = await create(call, "Archive replacement canary.")
    path = project.root / replacement["path"]
    data = path.read_text(encoding="utf-8")
    self.assertNotIn("\nrelations:", data)
    path.write_text(
        data.replace(
            "\n---\n",
            f"\nrelations:\n  IS_REPLACEMENT_FOR: [{atom}]\n---\n",
            1,
        ),
        encoding="utf-8",
    )
    relation_sql = (
        "SELECT source_ref, target_ref FROM relations WHERE source_kind = 'Atom' "
        f"AND source_ref = '{replacement['atom_id']}' AND target_kind = 'Atom' "
        f"AND target_ref = '{atom}' AND relation_type = 'IS_REPLACEMENT_FOR' AND NOT derived"
    )
    await asyncio.to_thread(
        project._wait_rows,
        relation_sql,
        [[replacement["atom_id"], atom]],
    )
    archived = await call("atom_lifecycle_archive", arguments)
    self.assertEqual("archived", archived["artifact"]["status"])
    self.assertEqual(
        [[f"{atom}@{original['version']}", "archived"]],
        project._rows(sql),
    )
