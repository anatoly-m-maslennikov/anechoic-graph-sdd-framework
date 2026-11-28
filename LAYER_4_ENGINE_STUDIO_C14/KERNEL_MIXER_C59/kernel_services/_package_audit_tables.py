"""Create Package audit tables in the caller transaction."""

from collections import defaultdict


def create_package_audit(connection):
    connection.execute(
        "CREATE TABLE IF NOT EXISTS main.package_audit "
        "(package_key VARCHAR, relative_path VARCHAR, has_internal BOOLEAN, "
        "has_public BOOLEAN, has_spec_bind BOOLEAN, binding_status VARCHAR, "
        "all_pins_active BOOLEAN, pin_issues JSON, contract_ref VARCHAR, "
        "contract_covered BOOLEAN)"
    )
    connection.execute(
        "ALTER TABLE main.package_audit ADD COLUMN IF NOT EXISTS "
        "test_issue VARCHAR"
    )
    connection.execute(
        "ALTER TABLE main.package_audit ADD COLUMN IF NOT EXISTS "
        "component_contracts JSON"
    )


def _pin_issues(entries, exact, selection):
    issues, resolved = [], []
    for kind, ref in entries:
        row, reason = exact.get(ref), None
        if row is not None:
            if not row["id"].startswith(selection.project_prefix + "-S-"):
                reason = "non_spec"
            elif row["status_group"] != "Current":
                reason = (
                    "archived"
                    if row["status_group"] == "Archived"
                    else "missing"
                )
            else:
                resolved.append((kind, row["_exact_ref"]))
        elif reason is None:
            reason = "missing"
        if reason:
            issues.append(
                {"entry_kind": kind, "reference": ref, "reason": reason}
            )
    return issues, resolved


def _test_issue(key, path, test_packages, test_sources, test_targets, markers):
    test_issue = None
    if key in test_packages and key not in test_sources:
        test_issue = "missing_test_target"
    elif key in test_targets and not markers[path]:
        test_issue = "missing_visibility_marker"
    return test_issue


def _load_pins(connection, binding_states):
    pins = defaultdict(list)
    for owner, kind, atom, version in connection.execute(
        "SELECT owner_path, entry_kind, atom_id, version FROM "
        "main.implementation_rmedo"
    ).fetchall():
        if binding_states.get(owner) == "valid":
            pins[owner].append((kind, f"{atom}@{version}"))

    return pins
