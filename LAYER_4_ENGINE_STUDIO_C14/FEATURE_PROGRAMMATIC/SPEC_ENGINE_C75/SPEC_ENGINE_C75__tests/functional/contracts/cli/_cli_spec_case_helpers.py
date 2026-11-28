def _check_subcommands(
    self, root, pins, path, original, bypass, generic, check_cli_spec
):
    for body, verdict in (
        (original, "matched"),
        (
            original.replace(
                "'kind': 'effect', 'target': 'C2'",
                "'kind': 'effect', 'target': 'C3'",
            ),
            "conflicting",
        ),
        (
            original.replace("'invoking': {'on': {", bypass),
            "conflicting",
        ),
        (
            original.replace("'running': {'on': {'select':", generic),
            "conflicting",
        ),
    ):
        path.write_text(body, encoding="utf-8")
        report = check_cli_spec(root, "C2", *pins, interface="suite")
        direction = report["directions"]["contract_solution"]
        self.assertEqual(verdict, direction["status"])


def _check_query(
    self,
    root,
    pins,
    solution,
    original,
    bypass,
    initial_bypass,
    check_cli_spec,
):
    for old, new, key, verdict in (
        (
            "exact_name_match",
            "body_match",
            "guarantees.priority",
            "conflicting",
        ),
        (
            "['trace', 'records']",
            "['records']",
            "output_fields",
            "conflicting",
        ),
        (
            "'running': {'on': {",
            bypass,
            "guarantees.priority",
            "unresolved",
        ),
        (
            "'idle': {'on': {",
            initial_bypass,
            "interface",
            "unresolved",
        ),
    ):
        with self.subTest(verdict=verdict):
            solution.write_text(
                original.replace(old, new, 1), encoding="utf-8"
            )
            report = check_cli_spec(root, "C2", *pins, interface="suite")
            facts = report["directions"]["contract_solution"]["facts"]
            fact = next(row for row in facts if row["key"] == key)
            self.assertEqual(verdict, fact["status"])


def _subcommand_route():
    return (
        "'running': {'on': {'select': {'target': "
        "'invoking', 'guard': {'type': 'matchesTrace',\n"
        "            'params': {'kind': 'trigger', "
        "'detail': {'command': 'local'}}}}}},\n"
        "        'invoking': {'on': {'dispatch': "
        "{'target': 'reporting', 'guard': {'type': "
        "'matchesTrace',\n"
        "            'params': {'kind': 'effect', "
        "'target': 'C2'}}}}},\n"
        "        'reporting': {'on': {"
    )
