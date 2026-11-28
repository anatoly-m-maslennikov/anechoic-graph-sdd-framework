"""Lifecycle action sequences for the latency fixture."""


async def _task_initial(self, client, samples, target, SUMMARY):
    draft = await self._run(
        client,
        samples,
        "Create Task Draft",
        "create_draft",
        {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": SUMMARY,
            }
        },
        "draft",
    )
    atom = draft.split("@")[0]
    await self._run(
        client,
        samples,
        "Publish Task Draft",
        "promote_draft",
        {
            "target": target(draft),
            "targetStatus": "backlog",
        },
        "backlog",
        f"{atom}@1",
    )
    await self._run(
        client,
        samples,
        "Queue Task",
        "change_status",
        {
            "target": target(atom),
            "targetStatus": "in_queue",
        },
        "in_queue",
        f"{atom}@1",
    )
    return atom


async def _task_revision(self, client, samples, target, SUMMARY, atom):
    revised = await self._run(
        client,
        samples,
        "Revise Task",
        "update",
        {
            "sourceCurrent": target(atom),
            "changes": {"body": SUMMARY + "\nRevised.\n"},
        },
        "draft",
        f"{atom}@2-draft",
    )
    await self._run(
        client,
        samples,
        "Publish Task revision",
        "promote_draft",
        {
            "target": target(revised, 2),
            "targetStatus": "backlog",
        },
        "backlog",
        f"{atom}@2",
    )


async def task(self, client, samples, target, SUMMARY):
    atom = await _task_initial(self, client, samples, target, SUMMARY)
    await _task_revision(self, client, samples, target, SUMMARY, atom)


async def _contract_initial(self, client, samples, target, CONTRACT):
    draft = await self._run(
        client,
        samples,
        "Create Contract Draft",
        "create_draft",
        {
            "newAtom": {
                "template": "component_contract",
                "container": {"component": "C00"},
                "lens": "SPEC",
                "body": CONTRACT,
            }
        },
        "draft",
    )
    atom = draft.split("@")[0]
    await self._run(
        client,
        samples,
        "Publish Contract Draft",
        "promote_draft",
        {
            "target": target(draft),
            "targetStatus": "ready",
        },
        "ready",
        f"{atom}@1",
    )
    await self._run(
        client,
        samples,
        "Activate Contract",
        "change_status",
        {
            "target": target(atom),
            "targetStatus": "active",
        },
        "active",
        f"{atom}@1",
    )
    return atom


async def _contract_revision(self, client, samples, target, CONTRACT, atom):
    revised = await self._run(
        client,
        samples,
        "Revise Contract",
        "update",
        {
            "sourceCurrent": target(atom),
            "changes": {"body": CONTRACT + "\nRevised.\n"},
        },
        "draft",
        f"{atom}@2-draft",
    )
    await self._run(
        client,
        samples,
        "Archive Contract Draft",
        "archive",
        {
            "target": target(revised, 2),
        },
        "archived",
        f"{atom}@2",
    )
    await self._run(
        client,
        samples,
        "Archive Active Contract",
        "archive",
        {
            "target": target(atom),
        },
        "archived",
        f"{atom}@1",
    )


async def contract(self, client, samples, target, CONTRACT):
    atom = await _contract_initial(self, client, samples, target, CONTRACT)
    await _contract_revision(self, client, samples, target, CONTRACT, atom)
