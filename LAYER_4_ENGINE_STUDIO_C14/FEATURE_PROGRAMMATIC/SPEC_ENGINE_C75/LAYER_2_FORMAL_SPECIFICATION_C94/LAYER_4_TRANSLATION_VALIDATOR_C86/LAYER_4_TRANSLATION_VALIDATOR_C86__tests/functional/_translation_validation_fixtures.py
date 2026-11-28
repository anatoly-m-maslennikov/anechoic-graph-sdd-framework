CONTRACT = (
    "declare_trace_contract(action='invoke', output='done', "
    "must_effect=(\n"
    "    ('store', 'saved', {'flag': False, 'zero': 0, "
    "'nothing': None, 'text': 'λ\"\\\\\\n\\t'}),))"
)
SOLUTION = (
    "component_workflow(component='C52', action='invoke', "
    "machine={\n"
    "    'id': 'invoke', 'initial': 'start', 'states': {\n"
    "        'start': {'on': {'finish': {'target': 'done', "
    "'guard': {\n"
    "            'type': 'matchesTrace', 'params': {'kind': "
    "'output', 'outcome': 'done',\n"
    "                                              "
    "'detail': {'fraction': 1.0}}}}}},\n"
    "        'done': {'type': 'final'}}})"
)


def model():
    boundaries = {"state": {"reads": [], "writes": []}}
    return {
        "component_id": "C52",
        "manifest": {
            "source": {"atom_id": "M"},
            "fields": {
                "component_id": "C52",
                "name": "Core",
                "boundaries": boundaries,
            },
            "boundaries": boundaries,
        },
        "contract": {
            "source": {"atom_id": "C"},
            "claims": [("python trace", CONTRACT)],
        },
        "solution": {
            "source": {"atom_id": "S"},
            "claims": [("python", SOLUTION)],
        },
    }


def mutate(program):
    target = r"flag\": false"
    if program.count(target) != 1:
        raise AssertionError(
            "Expected the contract flag in the emitted Lean program"
        )
    return program.replace(target, r"flag\": true ", 1)


def compared(loaded, compiled, *, mermaid, action, observe, **options):
    observe(compiled["claims"], action, "trace")
    return {
        "status": "matched",
        "mermaid": mermaid,
        "sources": {
            role: loaded[role]["source"]
            for role in ("manifest", "contract", "solution")
        },
    }
