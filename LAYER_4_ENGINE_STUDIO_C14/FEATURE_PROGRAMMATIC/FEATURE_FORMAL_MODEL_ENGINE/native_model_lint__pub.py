"""Check native Model Declaration references against a supplied catalog."""

from __future__ import annotations

import re
from collections.abc import Collection, Callable, Mapping

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE._native_model_lint_paths import (
    _validate_fallback,
    _validate_paths,
    _validate_population,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.python.dataclass_field_contract__pub import (
    validate_field_contracts,
)


def lint_native_model_claim(
    declaration: dict,
    *,
    declared_addresses: Collection[str],
    relation_names: Collection[str],
    path: str,
    first_line: int,
    resolve_address: Callable,
    simple_address: Callable,
    canonical_address: Callable,
    python_class_bindings: Mapping[str, Collection[str]] | None = None,
) -> tuple[str, ...]:
    lint = native_model_claim_linter(
        declared_addresses=declared_addresses,
        relation_names=relation_names,
        resolve_address=resolve_address,
        simple_address=simple_address,
        canonical_address=canonical_address,
        python_class_bindings=python_class_bindings,
    )
    return lint(declaration, path, first_line)


def native_model_claim_linter(
    *,
    declared_addresses: Collection[str],
    relation_names: Collection[str],
    resolve_address: Callable,
    simple_address: Callable,
    canonical_address: Callable,
    python_class_bindings: Mapping[str, Collection[str]] | None = None,
) -> Callable[[dict, str, int], tuple[str, ...]]:
    """Prepare the address catalog once for a set of Claims."""
    declared, canonical, class_names = _catalog(
        declared_addresses, simple_address, canonical_address
    )

    def lint(declaration: dict, path: str, first_line: int) -> tuple[str, ...]:
        args = declaration["arguments"]
        line = first_line + declaration["line"] - 1

        def error(message: str) -> tuple[str, ...]:
            return (f"{path}:{line}:1: {message}",)

        result = _validate_preliminary(
            declaration,
            args,
            python_class_bindings,
            canonical_address,
            canonical,
            class_names,
            relation_names,
            simple_address,
            declared,
            error,
        )
        if result:
            return result
        return _validate_remaining(
            declaration,
            args,
            relation_names,
            resolve_address,
            canonical_address,
            canonical,
            declared,
            error,
        )

    return lint


def _validate_remaining(
    declaration,
    args,
    relation_names,
    resolve_address,
    canonical_address,
    canonical,
    declared,
    error,
):
    result = _validate_population(
        args,
        canonical_address,
        canonical,
        resolve_address,
        declared,
        relation_names,
        error,
    )
    if result:
        return result
    return _validate_paths(
        declaration,
        args,
        relation_names,
        resolve_address,
        canonical_address,
        canonical,
        declared,
        error,
    )


def _validate_preliminary(
    declaration,
    args,
    python_class_bindings,
    canonical_address,
    canonical,
    class_names,
    relation_names,
    simple_address,
    declared,
    error,
):
    result = _validate_claim(
        declaration,
        args,
        python_class_bindings,
        canonical_address,
        canonical,
        class_names,
        error,
    )
    if result:
        return result
    result = _validate_fallback(
        args,
        relation_names,
        canonical_address,
        canonical,
        simple_address,
        declared,
        error,
    )
    if result:
        return result
    return ()


def _catalog(declared_addresses, simple_address, canonical_address):
    declared = set()
    canonical = set()
    class_names: dict[str, set[str]] = {}
    for address in declared_addresses:
        try:
            canonical.add(canonical_address(address))
        except ValueError:
            pass
        try:
            simple = simple_address(address)
        except ValueError:
            simple = None
        if simple is not None:
            declared.add(simple)
            if "." not in simple and "//" not in simple:
                name = re.sub(
                    r"[^a-z0-9]", "", simple.rsplit("/", 1)[-1].casefold()
                )
                class_names.setdefault(name, set()).add(
                    re.sub(r"\s+", "", simple).casefold()
                )
        qualifier = re.search(
            r"/\(\.Header\.Context\.(?:Role|Form)\s*:=\s*([^)]*)\)\s*$",
            address,
        )
        if qualifier:
            name = re.sub(r"[^a-z0-9]", "", qualifier[1].casefold())
            class_names.setdefault(name, set()).add(
                re.sub(r"\s+", "", address).casefold()
            )
    return declared, canonical, class_names


def _validate_instance_check(declaration, args, error):
    check = declaration.get("instance_check")
    if check is not None:
        model_type = check["parameter_type"]
        local_classes = {item["name"] for item in declaration["classes"]}
        if (
            model_type not in local_classes
            and declaration["imports"].get(model_type) != "anechoic.model"
        ):
            return error(
                f"instance check requires a Model class: {model_type}"
            )
        entity_class = args.get("entity_class")
        if entity_class is not None and model_type != entity_class:
            return error(
                f"instance check does not match entity_class: {model_type}"
            )

    return ()


def _validate_imports(
    declaration,
    python_class_bindings,
    canonical_address,
    canonical,
    class_names,
    error,
):
    for name, module in declaration["imports"].items():
        if module == "anechoic.model":
            if (
                python_class_bindings is not None
                and name in python_class_bindings
            ):
                targets = python_class_bindings[name]
                if isinstance(targets, str) or not isinstance(
                    targets, Collection
                ):
                    return error(f"invalid Model class binding: {name}")
                try:
                    matches = {canonical_address(target) for target in targets}
                except ValueError, TypeError:
                    return error(f"invalid Model class binding: {name}")
                if matches - canonical:
                    return error(f"unknown Model class address: {name}")
            else:
                matches = class_names.get(
                    re.sub(r"[^a-z0-9]", "", name.casefold()), set()
                )
            if not matches:
                return error(f"unknown Model class: {name}")
            if len(matches) > 1:
                return error(f"ambiguous Model class: {name}")
    return ()


def _validate_claim(
    declaration,
    args,
    python_class_bindings,
    canonical_address,
    canonical,
    class_names,
    error,
):
    try:
        validate_field_contracts(declaration)
    except ValueError as failure:
        return error(str(failure))

    result = _validate_instance_check(declaration, args, error)
    if result:
        return result

    return _validate_imports(
        declaration,
        python_class_bindings,
        canonical_address,
        canonical,
        class_names,
        error,
    )
