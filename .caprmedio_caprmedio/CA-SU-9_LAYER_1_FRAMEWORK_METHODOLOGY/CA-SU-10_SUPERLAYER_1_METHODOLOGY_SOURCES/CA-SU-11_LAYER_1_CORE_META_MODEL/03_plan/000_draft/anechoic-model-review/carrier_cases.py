"""Executable review cases for Atom identity, filenames, and Project tree placement."""

import re
from functools import partial
from pathlib import PurePosixPath

from structure_cases import project_tree, rejected


FAMILY_TREES = {"S": "SPEC", "T": "TKT", "P": "PMETA"}
CURRENT_STATUSES = {
    "SPEC": {"active"},
    "TKT": {"backlog", "active", "done", "canceled", "resolved"},
    "PMETA": {"active"},
}
HISTORICAL_GROUPS = {"draft": "Draft", "archived": "Archived"}


def filename_token(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*", value
    ):
        raise ValueError("Invalid lens or template filename token")
    return re.sub(r"[ _-]", "_", value).upper()


def summary_slug(summary):
    if not isinstance(summary, str) or not summary.isprintable():
        raise ValueError("Expected a printable Summary")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", summary).strip("-").lower()
    if not slug:
        raise ValueError("Summary has no ASCII letters or digits")
    return slug


def derive_carrier(atom_id, version, status, summary, *, project_prefix="AN",
                   lens=None, template=None, package_id=None):
    if not isinstance(atom_id, str) or type(version) is not int or version < 1:
        raise ValueError("Invalid stable Atom ID or Version")
    match = re.fullmatch(rf"{re.escape(project_prefix)}-([STP])-[0-9]+", atom_id)
    if not match:
        raise ValueError("Invalid stable Atom ID")
    family = FAMILY_TREES[match[1]]
    if not isinstance(status, str):
        raise ValueError("Expected a Status name")
    if status in CURRENT_STATUSES[family]:
        group = "Current"
    elif status in HISTORICAL_GROUPS:
        group = HISTORICAL_GROUPS[status]
    else:
        raise ValueError("Status does not belong to this Atom family")

    suffix = "-draft" if group == "Draft" else ""
    exact_ref = f"{atom_id}@{version}{suffix}"
    marker = atom_id if group == "Current" else exact_ref
    lens_token = filename_token(lens) if lens is not None else None
    template_token = filename_token(template) if template is not None else None
    if template_token == "PKG" and (
        family != "SPEC" or not isinstance(package_id, str) or not package_id.strip()
    ):
        raise ValueError("A PKG carrier needs a SPEC identity and an explicit Package ID")
    stem = "-".join(token for token in (marker, lens_token, template_token) if token)
    return family, group, exact_ref, f"{stem}--{summary_slug(summary)}.md"


def carrier_directory(project_name, family, status, lens, spec_section, ticket_branch,
                      linked_ticket_directory=None):
    records = PurePosixPath(f".anechoic_{project_name}")
    if family == "SPEC":
        if not spec_section:
            raise ValueError("SPEC needs an owning Component Spec Section")
        directory = filename_token(lens) if status == "active" else status
        return PurePosixPath(spec_section) / directory
    if family == "TKT":
        tickets = records / "__TKT"
        if linked_ticket_directory is not None:
            directory = PurePosixPath(linked_ticket_directory)
            if not directory.is_relative_to(tickets):
                raise ValueError("Linked Ticket directory belongs to another tree")
            parts = directory.relative_to(tickets).parts
            if (len(parts) not in (1, 2) or parts[0] not in {"TASKS", "ISSUES"}
                    or (ticket_branch is not None and parts[0] != ticket_branch)
                    or (len(parts) == 2 and parts[1] not in (
                        CURRENT_STATUSES["TKT"] - {"active"} | HISTORICAL_GROUPS.keys()))):
                raise ValueError("Linked Ticket directory is invalid")
            return directory
        if ticket_branch not in {"TASKS", "ISSUES", "ASSETS"}:
            raise ValueError("TKT needs a Task, Issue, or standalone Asset branch")
        branch = tickets / ticket_branch
        return branch if status == "active" else branch / status
    base = records / "_PMETA"
    return base if status == "active" else base / status


def validate_carrier(relative_path, project_name, observed_group, observed_ref,
                     fields, *, enabled_lenses=(), spec_section=None, ticket_branch=None,
                     linked_ticket_directory=None):
    family, group, exact_ref, basename = derive_carrier(**fields)
    lens = fields.get("lens")
    if lens is not None and lens not in enabled_lenses:
        raise ValueError("Lens is not enabled for the containing Component")
    if project_tree(relative_path, project_name) != family:
        raise ValueError("Atom ID family disagrees with its logical Project tree")
    if observed_group != group or observed_ref != exact_ref:
        raise ValueError("Status group or exact reference disagrees with the Header")
    if PurePosixPath(relative_path).name != basename:
        raise ValueError("Basename disagrees with the Header or Summary")
    directory = carrier_directory(project_name, family, fields["status"], lens,
                                  spec_section, ticket_branch, linked_ticket_directory)
    if PurePosixPath(relative_path).parent != directory:
        raise ValueError("Physical carrier directory disagrees with its owner, lens, or status")
    return group, exact_ref, basename


def select_revision(reference, revisions):
    matches = [
        (group, exact)
        for group, exact in revisions
        if reference == exact or (group == "Current" and reference == exact.split("@")[0])
    ]
    if len(matches) > 1:
        raise ValueError("Atom reference is ambiguous")
    return matches[0] if matches else None


CASES = (
    # ID, Version, Status, Lens, Template, Summary, Group, exact reference, basename
    ("AN-S-123", 2, "active", "DES", "DECISION", "Bound query latency", "Current",
     "AN-S-123@2", "AN-S-123-DES-DECISION--bound-query-latency.md"),
    ("AN-S-123", 3, "draft", "DES", "DECISION", "Bound query latency", "Draft",
     "AN-S-123@3-draft", "AN-S-123@3-draft-DES-DECISION--bound-query-latency.md"),
    ("AN-S-123", 1, "archived", "DES", "DECISION", "Bound query latency", "Archived",
     "AN-S-123@1", "AN-S-123@1-DES-DECISION--bound-query-latency.md"),
    ("AN-T-8", 2, "active", None, "TASK", "Review query latency", "Current",
     "AN-T-8@2", "AN-T-8-TASK--review-query-latency.md"),
    ("AN-T-8", 3, "draft", None, "TASK", "Review query latency", "Draft",
     "AN-T-8@3-draft", "AN-T-8@3-draft-TASK--review-query-latency.md"),
    ("AN-T-8", 1, "archived", None, "TASK", "Review query latency", "Archived",
     "AN-T-8@1", "AN-T-8@1-TASK--review-query-latency.md"),
    ("AN-P-9", 3, "active", None, "WORKFLOW", "Run local release", "Current",
     "AN-P-9@3", "AN-P-9-WORKFLOW--run-local-release.md"),
    ("AN-P-9", 2, "draft", None, "WORKFLOW", "Run local release", "Draft",
     "AN-P-9@2-draft", "AN-P-9@2-draft-WORKFLOW--run-local-release.md"),
    ("AN-P-9", 2, "archived", None, "WORKFLOW", "Run local release", "Archived",
     "AN-P-9@2", "AN-P-9@2-WORKFLOW--run-local-release.md"),
    ("AN-S-124", 2, "active", "SWE", "PKG", "Create order", "Current",
     "AN-S-124@2", "AN-S-124-SWE-PKG--create-order.md"),
    ("AN-S-124", 3, "draft", None, "PKG", "Create order", "Draft",
     "AN-S-124@3-draft", "AN-S-124@3-draft-PKG--create-order.md"),
    ("AN-S-124", 1, "archived", "SPEC", "PKG", "Create order", "Archived",
     "AN-S-124@1", "AN-S-124@1-SPEC-PKG--create-order.md"),
)


def run_cases():
    records = ".anechoic_anechoic"
    areas = {"S": f"{records}/LEXER_C43", "T": f"{records}/__TKT/TASKS",
             "P": f"{records}/_PMETA"}
    placements = {
        "S": {"draft": "draft", "archived": "archived"},
        "T": {"active": "", "draft": "draft", "archived": "archived"},
        "P": {"active": "", "draft": "draft", "archived": "archived"},
    }
    revisions = []
    for atom_id, version, status, lens, template, summary, group, exact, filename in CASES:
        fields = dict(atom_id=atom_id, version=version, status=status, summary=summary,
                      lens=lens, template=template, package_id="pkg3344" if template == "PKG" else None)
        family = atom_id.split("-")[1]
        directory = lens if family == "S" and status == "active" else placements[family][status]
        path = PurePosixPath(areas[family]) / directory / filename
        assert validate_carrier(path, "anechoic", group, exact, fields,
                                enabled_lenses={"DES", "SWE", "SPEC"}, spec_section=areas["S"],
                                ticket_branch="TASKS") == (group, exact, filename)
        revisions.append((group, exact))

    assert select_revision("AN-S-123", revisions) == ("Current", "AN-S-123@2")
    assert select_revision("AN-S-123@2", revisions) == ("Current", "AN-S-123@2")
    assert select_revision("AN-P-9@2", revisions) == ("Archived", "AN-P-9@2")
    assert select_revision("AN-P-9@2-draft", revisions) == ("Draft", "AN-P-9@2-draft")
    assert select_revision("AN-S-123@3", revisions) is None
    assert select_revision("AN-S-123-DES@2", revisions) is None
    assert select_revision("AN-T-8", [("Archived", "AN-T-8@1")]) is None
    rejected(select_revision, "AN-T-8", [("Current", "AN-T-8@2"), ("Current", "AN-T-8@3")])

    spec = dict(atom_id="AN-S-123", version=2, status="active", summary="Bound query latency",
                lens="DES", template="DECISION")
    basename = "AN-S-123-DES-DECISION--bound-query-latency.md"
    path = f"{areas['S']}/DES/{basename}"
    rejected(validate_carrier, path, "anechoic", "Current", "AN-S-123@2", spec)
    with_des = partial(validate_carrier, enabled_lenses={"DES"}, spec_section=areas["S"])
    for other_tree in (f"{records}/__TKT", f"{records}/_PMETA", "engine"):
        rejected(with_des, f"{other_tree}/{basename}", "anechoic", "Current",
                 "AN-S-123@2", spec)
    for wrong_directory in ("", "SWE", "draft", "archived"):
        wrong_path = PurePosixPath(areas["S"]) / wrong_directory / basename
        rejected(with_des, wrong_path, "anechoic", "Current", "AN-S-123@2", spec)

    ticket = dict(atom_id="AN-T-8", version=2, status="active",
                  summary="Review query latency", template="TASK")
    ticket_path = f"{areas['T']}/AN-T-8-TASK--review-query-latency.md"
    assert derive_carrier(**ticket) == derive_carrier(**(ticket | {"status": "done"}))
    for branch, template, cases in (
        ("TASKS", "TASK", (("done", "done"), ("canceled", "canceled"), ("backlog", "backlog"))),
        ("ISSUES", "ISSUE", (("active", ""), ("draft", "draft"),
                             ("archived", "archived"), ("resolved", "resolved"),
                             ("backlog", "backlog"))),
    ):
        checked = partial(validate_carrier, ticket_branch=branch)
        other = "ISSUES" if branch == "TASKS" else "TASKS"
        for status, directory in cases:
            fields = ticket | {"template": template, "status": status}
            _, group, exact, filename = derive_carrier(**fields)
            base = PurePosixPath(records) / "__TKT"
            assert checked(base / branch / directory / filename, "anechoic", group,
                           exact, fields) == (group, exact, filename)
            rejected(checked, base / other / directory / filename, "anechoic", group,
                     exact, fields)
            wrong = "done" if status == "active" else ""
            rejected(checked, base / branch / wrong / filename, "anechoic", group,
                     exact, fields)
    asset = ticket | {"atom_id": "AN-T-16", "status": "draft", "template": "Analysis Report"}
    _, group, exact, filename = derive_carrier(**asset)
    tasks = PurePosixPath(records) / "__TKT" / "TASKS"
    standalone = tasks.parent / "ASSETS" / "draft"
    assert validate_carrier(tasks / filename, "anechoic", group, exact, asset,
                            linked_ticket_directory=tasks) == (group, exact, filename)
    assert validate_carrier(standalone / filename, "anechoic", group, exact, asset,
                            ticket_branch="ASSETS") == (group, exact, filename)
    wrong = partial(validate_carrier, linked_ticket_directory=tasks.parent / "ASSETS")
    rejected(wrong, standalone / filename, "anechoic", group, exact, asset)
    rejected(validate_carrier, ticket_path, "anechoic", "Draft", "AN-T-8@2", ticket)
    rejected(validate_carrier, ticket_path, "anechoic", "Current", "AN-T-8", ticket)
    rejected(validate_carrier, ticket_path, "billing", "Current", "AN-T-8@2", ticket)
    for status, group, ref, wrong_marker in (
        ("active", "Current", "AN-T-8@2", "AN-T-8@2"),
        ("draft", "Draft", "AN-T-8@2-draft", "AN-T-8@2"),
        ("archived", "Archived", "AN-T-8@2", "AN-T-8@2-draft"),
    ):
        wrong_path = f"{areas['T']}/{wrong_marker}-TASK--review-query-latency.md"
        rejected(validate_carrier, wrong_path, "anechoic", group, ref, ticket | {"status": status})

    assert derive_carrier("AN-S-01", 2, "active", "Valid summary")[2:] == (
        "AN-S-01@2", "AN-S-01--valid-summary.md")
    assert derive_carrier("AN-S-0", 1, "active", "Valid summary")[2] == "AN-S-0@1"
    for atom_id, version, status in (("AN-R-1", 2, "active"), ("CA-S-1", 2, "active"),
                                     ("AN-S-", 2, "active"), ("AN-S-1", 0, "active"),
                                     ("AN-S-1", True, "active"), ("AN-P-1", 1, "done")):
        rejected(derive_carrier, atom_id, version, status, "Valid summary")
    rejected(partial(derive_carrier, template="PKG"), "AN-S-124", 2, "active", "Create order")
    rejected(partial(derive_carrier, template="PKG", package_id="pkg3344"),
             "AN-P-124", 2, "active", "Create order")
    rejected(filename_token, "DES/DOM")
    assert filename_token("work log") == "WORK_LOG"
    assert summary_slug("DRY — Don’t Repeat Yourself") == "dry-don-t-repeat-yourself"
    rejected(summary_slug, "—")
    rejected(summary_slug, "two\nlines")
    validate_carrier(".anechoic_billing/__TKT/TASKS/BL-T-1--review.md", "billing", "Current",
                     "BL-T-1@1", dict(atom_id="BL-T-1", version=1, status="active",
                                      summary="Review", project_prefix="BL"), ticket_branch="TASKS")


if __name__ == "__main__":
    run_cases()
    print(f"{len(CASES)} carrier examples and agreement rejection cases passed")
