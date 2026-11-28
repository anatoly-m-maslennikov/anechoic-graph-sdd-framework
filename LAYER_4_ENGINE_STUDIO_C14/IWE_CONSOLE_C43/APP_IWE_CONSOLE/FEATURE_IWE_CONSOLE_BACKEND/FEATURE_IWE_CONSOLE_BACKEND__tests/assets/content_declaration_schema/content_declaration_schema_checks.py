"""Assertions for the prepared reference transform fixture."""


def check_replacements(source):
    assert source.replacement("Ref ID") == "Identity.Ref ID"
    assert source.replacement("RefID") == "Identity.RefID"
    assert source.replacement("Updated At") == "State.Updated At"
    assert source.replacement("UpdatedAt") == "State.UpdatedAt"
    assert source.replacement("Subjects") == "Context.Topics"
    assert (
        source.replacement("Subjects.Active") == "Context.Topics.Main Subject"
    )
    assert (
        source.replacement("Subjects.Passive") == "Context.Topics.Dependencies"
    )
    assert (
        source.replacement("Priority", "Concern") == "Context.Concern.Priority"
    )
    assert source.replacement("Priority", "Plan") is None
    text = "Atom/(.Header.Role: Plan)/(.Header.Form: X);"
    after, _, holds, _ = source.migrate(text)
    assert (
        after == "Atom/(.Header.Context.Role: Plan)/(.Header.Context.Form: X);"
        and not holds
    )
    typed = (
        "Atom/(.Header.Role: Plan)//$atom; $atom.Header.Work Sequence Number"
    )
    after, _, holds, _ = source.migrate(typed)
    assert (
        "$atom.Header.Context.Plan.Work Sequence Number" in after and not holds
    )
    assert source.transform(after) == after


def check_roles(source):
    role, _, holds, _ = source.migrate(
        "Atom/(.Header.Role: Concern).Header.Priority;"
    )
    assert (
        role
        == (
            "Atom/(.Header.Context.Role: Concern).Header.Context.Concern."
            "Priority;"
        )
        and not holds
    )
    relative, _, holds, _ = source.migrate(
        "UNIQUE(Atom//$atom, (.Header.ID, .Header.Version));"
    )
    assert (
        "(.Header.Identity.ID, .Header.State.Version)" in relative
        and not holds
    )
    subject, _, holds, _ = source.migrate(
        "Atom//$atom; $atom.Header.Subjects.Passive"
    )
    assert "$atom.Header.Context.Topics.Dependencies" in subject and not holds


def check_unchanged(source):
    bare = "Header.Subjects.Active"
    assert source.transform(bare) == bare
    assert (
        source.rewrite(next(iter(source.E240_PATHS)), bare)
        == "Header.Context.Topics.Main Subject"
    )
    reviewed_path = next(iter(source.BARE_COMMON_PATHS))
    assert (
        source.rewrite(reviewed_path, "Header.Container")
        == "Header.Context.Container"
    )
    assert (
        source.rewrite(reviewed_path, "Entity.Header.ID") == "Entity.Header.ID"
    )
    assert source.transform("Header.Container") == "Header.Container"
    sql_columns = (
        "header_context_plan header_context_plan_work_sequence_number"
    )
    assert source.transform(sql_columns) == sql_columns
    unchanged, _, holds, _ = source.migrate(
        "Atom.Header.Context.Role Entity.Header.ID Entity.Header.Status"
    )
    assert (
        unchanged
        == "Atom.Header.Context.Role Entity.Header.ID Entity.Header.Status"
        and not holds
    )
