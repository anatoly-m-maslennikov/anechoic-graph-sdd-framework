"""Executable model-review examples; these do not implement lifecycle operations."""


def content_edit_allowed(kind, status_group, source_id, target_id, target_group, in_place):
    if kind == "ticket_asset" and status_group in {"Draft", "Current"}:
        if in_place:
            return source_id == target_id and target_group == status_group
        raise ValueError("versioned Ticket asset edits are not settled here")
    if status_group == "Current":
        return not in_place and target_group == "Draft" and source_id == target_id
    raise ValueError("case outside the settled edit rules")


def status_transition_valid(old_id, old_version, new_id, new_version):
    return old_id == new_id and old_version == new_version


def ticket_records_valid(task, work_log, assets):
    records = [task, work_log, *assets]
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        return False
    return all(
        record["task_id"] == task["id"]
        and record["summary"] == task["summary"]
        and (task["epic"] is None or record["epic"] == task["epic"])
        for record in records[1:]
    )


def run_valid(workflow, run, existing_run_ids):
    return (
        workflow["area"] == "PMETA"
        and workflow["kind"] == "Workflow"
        and workflow["status"] == "Active"
        and run["workflow_id"] == workflow["id"]
        and run["workflow_revision"] == workflow["revision"]
        and bool(run["id"])
        and run["id"] not in existing_run_ids
    )


def governs_ticket(workflow_area, kind):
    return workflow_area == "PMETA" and kind == "Workflow"


def check():
    for kind in ("atom", "SPEC", "PMETA", "Task"):
        assert content_edit_allowed(kind, "Current", "A", "A", "Draft", False)
        assert not content_edit_allowed(kind, "Current", "A", "B", "Draft", False)
        assert not content_edit_allowed(kind, "Current", "A", "A", "Current", True)
    for group in ("Draft", "Current"):
        assert content_edit_allowed("ticket_asset", group, "L", "L", group, True)
        assert not content_edit_allowed("ticket_asset", group, "L", "other", group, True)
    assert status_transition_valid("T", 2, "T", 2)
    assert not status_transition_valid("T", 2, "T", 3)
    assert not status_transition_valid("T", 2, "U", 2)

    task = {"id": "T", "epic": "E", "summary": "Work"}
    log = {"id": "L", "epic": "E", "task_id": "T", "summary": "Work"}
    asset = {"id": "A", "epic": "E", "task_id": "T", "summary": "Work"}
    assert ticket_records_valid(task, log, [asset])
    assert not ticket_records_valid(task, log, [{**asset, "id": "L"}])
    assert not ticket_records_valid(task, log, [{**asset, "epic": "other"}])
    assert not ticket_records_valid(task, log, [{**asset, "task_id": "other"}])
    assert not ticket_records_valid(task, {**log, "summary": "other"}, [asset])
    assert not ticket_records_valid(task, log, [{**asset, "summary": "other"}])
    assert ticket_records_valid({**task, "epic": None}, log, [asset])

    workflow = {"id": "W", "area": "PMETA", "kind": "Workflow", "status": "Active", "revision": 2}
    run = {"id": "R2", "workflow_id": "W", "workflow_revision": 2}
    assert run_valid(workflow, run, {"R1"})
    assert not run_valid({**workflow, "status": "Draft"}, run, set())
    assert not run_valid({**workflow, "kind": "Step"}, run, set())
    assert not run_valid({**workflow, "area": "SPEC"}, run, set())
    assert not run_valid(workflow, {**run, "workflow_revision": 1}, set())
    assert not run_valid(workflow, {**run, "workflow_id": "other"}, set())
    assert not run_valid(workflow, run, {"R2"})
    assert governs_ticket("PMETA", "Workflow")
    assert not governs_ticket("PMETA", "Step")
    assert not governs_ticket("PMETA", "Action")
    assert not governs_ticket("SPEC", "Workflow")
    print("Lifecycle review-model acceptance cases passed")


if __name__ == "__main__":
    check()
