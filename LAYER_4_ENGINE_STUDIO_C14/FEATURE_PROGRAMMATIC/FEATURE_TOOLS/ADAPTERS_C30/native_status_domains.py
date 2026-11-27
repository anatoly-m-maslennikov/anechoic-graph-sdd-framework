"""Resolve Atom family Status values from admitted Model bindings."""

from .model_class_subject__pub import model_class_target


CURRENT_STATUSES = {
    "S": {"active", "ready"},
    "T": {"active", "in_queue", "backlog", "done", "canceled", "resolved", "complete"},
    "P": {"active"}, "C": {"active"},
}


def status_domains(bindings):
    declarations = bindings.get("declarations", [])
    if not isinstance(declarations, (list, tuple)):
        raise ValueError("Invalid Model declarations")
    names = {"Specification": "S", "Spec Atom": "S", "Ticket": "T", "Ticket Atom": "T",
             "project_config": "P", "Project Config Atom": "P"}
    targets = {}
    families = {"SpecAtom": "S", "TicketAtom": "T", "ProjectConfigAtom": "P"}
    for entry in declarations:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2 or not isinstance(entry[1], dict):
            raise ValueError("Invalid Model declaration")
        args = entry[1].get("arguments", {})
        if not isinstance(args, dict):
            raise ValueError("Invalid Model declaration arguments")
        class_name = args.get("entity_class")
        family = families.get(class_name) if isinstance(class_name, str) else None
        if family is not None:
            target = model_class_target(entry[0], args.get("entity_name"), require_namespace=False)
            if target is None or family in targets:
                raise ValueError("Invalid or duplicate Model Atom class declaration")
            targets[family] = target
    target_families = {target: family for family, target in targets.items()}
    domains = {}
    scoped_atom_status = False
    for entry in declarations:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2 or not isinstance(entry[1], dict):
            raise ValueError("Invalid Model declaration")
        args = entry[1].get("arguments", {})
        if not isinstance(args, dict):
            raise ValueError("Invalid Model declaration arguments")
        if args.get("entity_name") != "Status" or "applies_to_entity_classes" not in args:
            continue
        scopes, values = args["applies_to_entity_classes"], args.get("allowed_values")
        if not isinstance(scopes, (list, tuple)) or not scopes or any(not _string(scope) for scope in scopes):
            raise ValueError("Invalid scoped Model Status declaration")
        selected = []
        for scope in scopes:
            parent, sep, name = scope.rpartition("//")
            atom_status = (sep and name in names and (parent.endswith("/Atom") or parent.endswith("//Atom"))
                           and args.get("base_path") == parent + ".Header.State")
            scoped_atom_status = scoped_atom_status or bool(atom_status)
            family = target_families.get(scope) if targets else names.get(name)
            if (sep and family and (parent.endswith("/Atom") or parent.endswith("//Atom"))
                    and args.get("base_path") == parent + ".Header.State"):
                selected.append(family)
        if not selected:
            continue
        if (args.get("entity_kind") != "Property" or args.get("relation_name") != "IS_PROPERTY_OF"
                or not isinstance(values, (list, tuple)) or not values or any(not _string(value) for value in values)
                or len(set(values)) != len(values)):
            raise ValueError("Invalid scoped Model Status declaration")
        for family in selected:
            if family in domains:
                raise ValueError("Duplicate scoped Model Status declaration")
            domains[family] = set(values)
    if not domains and targets and scoped_atom_status:
        raise ValueError("Model Status scopes do not match Atom class declarations")
    if not domains:
        return {family: values | {"draft", "archived"} for family, values in CURRENT_STATUSES.items()}
    if targets and set(targets) != {"S", "T", "P"}:
        raise ValueError("Incomplete Model Atom class declarations")
    if set(domains) != {"S", "T", "P"}:
        raise ValueError("Incomplete scoped Model Status declarations")
    domains["C"] = domains["P"]
    return domains


def _string(value):
    return isinstance(value, str) and bool(value) and value == value.strip()
