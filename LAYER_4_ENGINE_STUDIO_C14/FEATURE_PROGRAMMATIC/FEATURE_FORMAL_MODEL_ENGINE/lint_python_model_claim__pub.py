"""Lint static Python Formal Claims against caller-supplied declarations.

Accepts Python files or Python fences under Claim / Formal Claim in Markdown.
The Model catalog is a JSON address array or an object with addresses and
python_classes bindings. The relation list can be a JSON array or the
Workbench registry object with a registered_names array. References with
complex qualifiers and instance selectors can be unsupported; the checker
validates selector Properties but does not evaluate their conditions. Callers
must provide unresolved symbolic Relation aliases explicitly.
Address bindings are caller-proven unique aliases to exact declared or
explicitly projected inherited addresses; they do not create declarations.
No Claim is executed. A block reports its first problem.
The direct CLI initializes the Engine path before importing its modules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from collections.abc import Collection, Mapping

_ENGINE = Path(__file__).resolve().parents[2]
if __package__ in (None, "") and str(_ENGINE) not in sys.path:
    sys.path.insert(0, str(_ENGINE))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (  # noqa: E402
    canonical_model_address,
    simple_model_address,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.python.python__shared import (  # noqa: E402
    PythonModelClaimError,
    parse_structured_python_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_lint._package__shared import (  # noqa: E402
    _address_catalog,
    _blocks,
    _names as _names,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (  # noqa: E402
    NativeModelClaimError,
    parse_native_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.native_model_lint__pub import (  # noqa: E402
    lint_native_model_claim,
)


from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_lint._package__shared import (  # noqa: E402
    _validate_exact_qualifiers,
    resolve_model_claim_reference as resolve_model_claim_reference,
)

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_lint._package__shared import (  # noqa: E402
    _check_relations,
    _project_bound_names,
)

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_lint._package__shared import (  # noqa: E402
    ReferenceValidator,
)


def _claim_error(error, path, first_line):
    message = str(error)
    match = re.match(r"line (\d+), column (\d+): (.*)", message, re.DOTALL)
    if match:
        return (
            f"{path}:{first_line + int(match[1]) - 1}:{match[2]}: {match[3]}",
        )
    return (f"{path}:{first_line}: {message}",)


def _simple_declared_addresses(
    declared_addresses, python_class_bindings, address_bindings
):
    declared = set()
    for address in declared_addresses:
        try:
            declared.add(simple_model_address(address))
        except ValueError:
            if python_class_bindings is None and address_bindings is None:
                raise
            canonical_model_address(address)
    return declared


def _prepare_addresses(
    declared_addresses,
    python_class_bindings,
    address_bindings,
    path,
    first_line,
):
    declared = _simple_declared_addresses(
        declared_addresses, python_class_bindings, address_bindings
    )
    return _bind_addresses(
        declared, declared_addresses, address_bindings, path, first_line
    )


def _bind_addresses(
    declared, declared_addresses, address_bindings, path, first_line
):
    exact_addresses: set[str] = set()
    bound_names: dict[str, str] = {}
    if address_bindings is not None:
        if not isinstance(address_bindings, Mapping):
            return None, (f"{path}:{first_line}: invalid address bindings",)
        exact_addresses = {
            canonical_model_address(address) for address in declared_addresses
        }
        for alias, target in address_bindings.items():
            if not isinstance(alias, str) or not isinstance(target, str):
                return None, (f"{path}:{first_line}: invalid address binding",)
            try:
                name = simple_model_address(alias)
                canonical_target = canonical_model_address(target)
            except ValueError:
                return None, (
                    f"{path}:{first_line}: invalid address binding: {alias}",
                )
            if (
                canonical_target not in exact_addresses
                or (name in exact_addresses and name != canonical_target)
                or (
                    name in bound_names
                    and bound_names[name] != canonical_target
                )
            ):
                return None, (
                    f"{path}:{first_line}: missing or ambiguous address binding: {alias}",
                )
            try:
                _validate_exact_qualifiers(
                    canonical_target, declared | exact_addresses
                )
            except ValueError as error:
                return None, (f"{path}:{first_line}: {error}",)
            bound_names[name] = canonical_target
        _project_bound_names(bound_names, exact_addresses)
        declared.update(bound_names)
        declared.update(exact_addresses)
    return (declared, exact_addresses, bound_names), ()


def _validate_legacy(text, validator, path, first_line):
    try:
        parse_structured_python_model_claim(
            text,
            validate_reference=validator.validate_reference,
            validate_relation_endpoint=validator.validate_relation_endpoint,
        )
    except PythonModelClaimError as error:
        return _claim_error(error, path, first_line)
    return ()


def _lint_legacy(
    text,
    declared_addresses,
    relation_names,
    path,
    first_line,
    relation_aliases,
    python_class_bindings,
    require_declared_aliases,
    address_bindings,
    relation_declaration,
):
    prepared, errors = _prepare_addresses(
        declared_addresses,
        python_class_bindings,
        address_bindings,
        path,
        first_line,
    )
    if errors:
        return errors
    declared, exact_addresses, bound_names = prepared
    validator = ReferenceValidator(
        declared,
        exact_addresses,
        bound_names,
        address_bindings,
        relation_names,
        relation_declaration,
    )
    errors = _validate_legacy(text, validator, path, first_line)
    if errors:
        return errors
    return _check_relations(
        text,
        relation_names,
        relation_aliases,
        require_declared_aliases,
        path,
        first_line,
    )


def _placement_result(text, path, first_line):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.placement_claim__pub import (
        parse_placement_rules,
    )

    try:
        if parse_placement_rules(text) is not None:
            return ()
    except ValueError as error:
        return (f"{path}:{first_line}: {error}",)
    return None


def lint_python_model_claim(
    text: str,
    *,
    declared_addresses: Collection[str],
    relation_names: Collection[str],
    path: str = "<claim>",
    first_line: int = 1,
    relation_aliases: Mapping[str, str] | None = None,
    python_class_bindings: Mapping[str, Collection[str]] | None = None,
    require_declared_aliases: bool = False,
    address_bindings: Mapping[str, str] | None = None,
    relation_declaration: str | None = None,
) -> tuple[str, ...]:
    """Return diagnostics; address aliases must bind declared addresses."""
    try:
        native = parse_native_model_claim(text)
    except NativeModelClaimError as error:
        return _claim_error(error, path, first_line)
    if native is not None:
        return lint_native_model_claim(
            native,
            declared_addresses=declared_addresses,
            relation_names=relation_names,
            path=path,
            first_line=first_line,
            resolve_address=resolve_model_claim_reference,
            simple_address=simple_model_address,
            canonical_address=canonical_model_address,
            python_class_bindings=python_class_bindings,
        )
    placement = _placement_result(text, path, first_line)
    if placement is not None:
        return placement
    return _lint_legacy(
        text,
        declared_addresses,
        relation_names,
        path,
        first_line,
        relation_aliases,
        python_class_bindings,
        require_declared_aliases,
        address_bindings,
        relation_declaration,
    )


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Python Claim files or Markdown carriers",
    )
    parser.add_argument(
        "--addresses",
        required=True,
        type=Path,
        help="JSON address array or Model catalog",
    )
    parser.add_argument(
        "--relations",
        required=True,
        type=Path,
        help="JSON array or Workbench relation registry",
    )
    parser.add_argument(
        "--relation-alias", action="append", default=[], metavar="TOKEN=NAME"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        addresses, class_bindings = _address_catalog(args.addresses)
        relations = _names(args.relations, registry=True)
        aliases = {}
        for entry in args.relation_alias:
            token, separator, name = entry.partition("=")
            if not separator or not token or not name:
                raise ValueError(f"invalid Relation alias: {entry}")
            aliases[token] = name
        diagnostics = []
        for path in args.paths:
            for block, first_line in _blocks(path):
                diagnostics.extend(
                    lint_python_model_claim(
                        block,
                        declared_addresses=addresses,
                        relation_names=relations,
                        path=str(path),
                        first_line=first_line,
                        relation_aliases=aliases,
                        python_class_bindings=class_bindings,
                    )
                )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    for diagnostic in diagnostics:
        print(diagnostic, file=sys.stderr)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
