_MANIFEST = """## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C2', name='Example', boundaries={'io': {'server': {'suite': {
        'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}))
```
"""
_CONTRACT = (
    "## Claim\n"
    "\n"
    "### Formal Claim\n"
    "\n"
    "```python cli\n"
    "declare_cli_contract(interface='suite', action='run', "
    "runner='uv', path='suite.py',\n"
    "                     outcomes={'succeeded': 'zero', "
    "'failed': 'nonzero'})\n"
    "```\n"
)
_SOLUTION = (
    "## Claim\n"
    "\n"
    "### Formal Claim\n"
    "\n"
    "```python\n"
    "component_workflow(component='C2', action='run', "
    "machine={\n"
    "    'id': 'suite', 'initial': 'idle', 'states': {\n"
    "        'idle': {'on': {'start': {'target': 'running', "
    "'guard': {'type': 'matchesTrace',\n"
    "            'params': {'kind': 'trigger', 'target': "
    "'suite',\n"
    "                       'detail': {'transport': 'cli', "
    "'runner': 'uv', 'path': 'suite.py'}}}}}},\n"
    "        'running': {'on': {\n"
    "            'pass': {'target': 'done', 'guard': "
    "{'type': 'matchesTrace', 'params':\n"
    "                {'kind': 'output', 'outcome': "
    "'succeeded', 'detail': {'exit_status_class': "
    "'zero'}}}},\n"
    "            'fail': {'target': 'done', 'guard': "
    "{'type': 'matchesTrace', 'params':\n"
    "                {'kind': 'output', 'outcome': "
    "'failed', 'detail': {'exit_status_class': "
    "'nonzero'}}}},\n"
    "        }},\n"
    "        'done': {'type': 'final'},\n"
    "    }})\n"
    "```\n"
)
_QUERY_CONTRACT = _CONTRACT.replace(
    "path='suite.py'", "module='engine.suite'"
).replace(
    "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
    (
        "arguments=('--query', '<text>'), "
        "output_fields=('records', 'trace'),\n"
        "    checks={'guarantees': {'priority': "
        "'exact_name_first'},\n"
        "            'effects': {'query_scope': "
        "'supplied_frozen_context'},\n"
        "            'output_format': {'record_properties': "
        "('admission_status', 'source_bindings')}}"
    ),
)
_QUERY_SOLUTION = (
    "## Claim\n"
    "\n"
    "### Formal Claim\n"
    "\n"
    "```python\n"
    "component_workflow(component='C2', action='run', "
    "machine={\n"
    "    'id': 'suite', 'initial': 'idle', 'states': {\n"
    "        'idle': {'on': {'start': {'target': 'running', "
    "'guard': {'type': 'matchesTrace',\n"
    "            'params': {'kind': 'trigger', 'target': "
    "'suite', 'detail': {\n"
    "                'transport': 'cli', 'runner': 'uv', "
    "'module': 'engine.suite',\n"
    "                'arguments': ['--query', "
    "'<text>']}}}}}},\n"
    "        'running': {'on': {\n"
    "            'search': {'target': 'reporting', 'guard': "
    "{'type': 'matchesTrace', 'params': {\n"
    "                'kind': 'effect', 'target': 'C2', "
    "'outcome': 'succeeded',\n"
    "                'detail': {'read_source': "
    "'context_argument', 'rank_first': "
    "'exact_name_match'}}}},\n"
    "        }},\n"
    "        'reporting': {'on': {\n"
    "            'return': {'target': 'done', 'guard': "
    "{'type': 'matchesTrace', 'params': {\n"
    "                'kind': 'output', 'outcome': "
    "'succeeded',\n"
    "                'detail': {'record_properties': "
    "['source_bindings', 'admission_status'],\n"
    "                           'output_fields': ['trace', "
    "'records']}}}},\n"
    "        }},\n"
    "        'done': {'type': 'final'},\n"
    "    }})\n"
    "```\n"
)


def _carrier(root, atom_id, template, owner, relations, body):
    path = root / f"{atom_id}.md"
    tier = {
        "component_manifest": 4,
        "component_contract": 0,
        "decision": 1,
        "solution": 0,
    }[template.casefold()]
    path.write_text(
        f"---\natom_family: SPEC\natom_id: {atom_id}"
        f"\ncontainer: {{component: {owner}}}"
        f"\ntier: {tier}\ncontext: {{template: {template}}}"
        f"\nrelations: {relations}"
        "\nstate: {status: active, version: 1}\n---\n\n" + body,
        encoding="utf-8",
    )
    return {
        "path": path.name,
        "atom_id": atom_id,
        "version": 1,
        "status": "active",
        "container_component": owner,
    }
