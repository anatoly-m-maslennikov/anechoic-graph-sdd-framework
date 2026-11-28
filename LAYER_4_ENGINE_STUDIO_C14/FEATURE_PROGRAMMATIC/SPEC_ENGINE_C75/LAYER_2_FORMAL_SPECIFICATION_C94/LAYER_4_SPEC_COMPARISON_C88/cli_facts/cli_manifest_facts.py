"""Extract declared CLI endpoint facts."""

from ._package__shared import _BINDING_FIELDS


def _manifest_facts(endpoint, interface):
    declared = (
        {
            "interface": interface,
            **{
                key: endpoint[key]
                for key in (*_BINDING_FIELDS, "subcommands")
                if key in endpoint
            },
        }
        if isinstance(endpoint, dict)
        else {}
    )
    if (
        isinstance(endpoint, dict)
        and isinstance(fields := endpoint.get("output_fields"), list)
        and all(isinstance(field, str) for field in fields)
    ):
        declared["output_fields"] = sorted(fields)
    if isinstance(endpoint, dict):
        declared.update(
            {
                key: endpoint[source]
                for key, source in (("stdin", "input"), ("stdout", "output"))
                if isinstance(endpoint.get(source), str) and endpoint[source].strip()
            }
        )
    if isinstance(endpoint, dict) and isinstance(endpoint.get("output"), dict):
        output = endpoint["output"]
        if output and all(
            isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
            for k, v in output.items()
        ):
            declared.update({f"stdout.{key}": value for key, value in output.items()})
    return declared
