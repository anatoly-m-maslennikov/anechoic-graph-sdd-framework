"""Read Relation contributions from Formal Claims."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import re
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import formal_claim_fences  # fmt: skip


_NAME = r"[A-Za-z_][A-Za-z_0-9]*"
_LITERAL_RELATION = re.compile(rf"Relation//({_NAME})\Z")
_BINDINGS = {"HAS_INVERSE", "IS_INVERSE_ALIAS_FOR"}


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class RegistryContribution:
    names: frozenset[str]
    inverses: tuple[tuple[str, str], ...]
    aliases: tuple[tuple[str, str], ...]


def _unsupported_metadata(source: str) -> None:
    print(
        (
            "Workbench: "
            f"{source}"
            ": unsupported Python relation metadata; link skipped"
        ),
        file=sys.stderr,
    )


def relation_declaration(body: str, source: str) -> RegistryContribution:
    names: set[str] = set()
    inverses: list[tuple[str, str]] = []
    aliases: list[tuple[str, str]] = []
    for language, claim in formal_claim_fences(body):
        if language != "python":
            continue
        contribution = _native_contribution(claim)
        if contribution is None:
            contribution = _helper_contribution(claim, source)
        names.update(contribution.names)
        inverses.extend(contribution.inverses)
        aliases.extend(contribution.aliases)
    return RegistryContribution(
        frozenset(names), tuple(inverses), tuple(aliases)
    )


def _helper_contribution(claim: str, source: str) -> RegistryContribution:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
        import parse_structured_python_model_claim  # fmt: skip

    names: set[str] = set()
    inverses: list[tuple[str, str]] = []
    aliases: list[tuple[str, str]] = []
    for call in parse_structured_python_model_claim(claim):
        helper, args = call["name"], call["arguments"]
        if helper == "relation":
            relation = args["name"]
            left = _literal_name(args["source"])
            if relation in _BINDINGS:
                right = _literal_name(args.get("target"))
                if left is None or right is None:
                    continue
                if (
                    call["scope"] == "instances"
                    or args.get("source_count") is not None
                    or args.get("target_count") is not None
                    or relation == "IS_INVERSE_ALIAS_FOR"
                    and args.get("reverse")
                ):
                    _unsupported_metadata(source)
                    continue
                if args.get("reverse"):
                    left, right = right, left
                if relation == "HAS_INVERSE":
                    names.update((left, right))
                    inverses.append((left, right))
                else:
                    names.add(right)
                    aliases.append((left, right))
            elif left is not None and args.get("source_count") is None:
                names.add(left)
        elif (
            helper == "subject_path"
            or helper == "classify"
            and args.get("notation") == "relation"
        ) and (name := _literal_name(args["address"])):
            names.add(name)
    return RegistryContribution(
        frozenset(names), tuple(inverses), tuple(aliases)
    )


def _literal_name(address: str | None) -> str | None:
    match = _LITERAL_RELATION.fullmatch(address) if address else None
    return match[1] if match else None


def _native_contribution(claim: str) -> RegistryContribution | None:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
        import parse_native_model_claim  # fmt: skip
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
        import emits_instance_inverse  # fmt: skip

    declaration = parse_native_model_claim(claim)
    if declaration is None:
        return None
    if declaration["kind"] != "relation":
        return RegistryContribution(frozenset(), (), ())
    arguments = declaration["arguments"]
    name = _relation_name(arguments["relation_name"])
    inverse = arguments.get("inverse_alias")
    if not inverse:
        return RegistryContribution(frozenset({name}), (), ())
    inverse = _relation_name(inverse)
    if emits_instance_inverse(arguments):
        return RegistryContribution(
            frozenset({name, inverse}), ((name, inverse),), ()
        )
    return RegistryContribution(frozenset({name}), (), ((inverse, name),))


def _relation_name(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(_NAME, value):
        raise ValueError(f"unsupported Relation name: {value!r}")
    return value
