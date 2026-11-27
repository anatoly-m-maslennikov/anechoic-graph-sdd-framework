"""Stateful callbacks for static legacy Claim references."""

from __future__ import annotations
import re
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared \
    import (
    canonical_model_address,
    simple_model_address,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared \
    import (
    RelationChain,
    namespace_local_expression,
    parse_subject_expression,
    render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    lint_python_model_claim_references \
    import (
    _SINGLETON_MEMBERSHIP,
    _requirement_form_selection,
    _validate_exact_qualifiers,
    resolve_model_claim_reference,
)  # fmt: skip


class ReferenceValidator:
    def __init__(
        self,
        declared,
        exact_addresses,
        bound_names,
        address_bindings,
        relation_names,
        relation_declaration,
    ):
        self.declared, self.exact_addresses, self.bound_names = (
            declared,
            exact_addresses,
            bound_names,
        )
        self.address_bindings, self.relation_names = (
            address_bindings,
            relation_names,
        )
        self.relation_declaration = relation_declaration
        self.bindings, self.generic = {}, set()

    def _normalize_reference(self, address):
        normalized = _SINGLETON_MEMBERSHIP.sub(
            lambda m: f"/(.{m[1]} := {m[2]})", address
        )
        try:
            expression = parse_subject_expression(
                normalized, subject_profile="approved"
            ).expression
            local = namespace_local_expression(expression)
            if local is not None and isinstance(expression, RelationChain):
                local_text = render_subject(local)
                local_base = re.sub(r"//\$[A-Za-z_]\w*$", "", local_text)
                if (
                    "/" in local_base
                    and local_base in self.bound_names
                    and render_subject(expression.endpoints[0])
                    not in self.exact_addresses
                ):
                    return None
        except ValueError:
            pass
        return normalized

    def _qualified_binding(self, normalized):
        variable = re.search(r"//(\$[A-Za-z_]\w*)$", normalized)
        base = normalized[: variable.start()] if variable else normalized
        try:
            canonical = canonical_model_address(base)
        except ValueError:
            return False
        if canonical not in self.exact_addresses:
            return False
        _validate_exact_qualifiers(base, self.declared)
        if variable:
            name = variable.group(1)[1:]
            if self.bindings.get(name, canonical) != canonical:
                raise ValueError(f"inconsistent binding: ${name}")
            self.bindings[name] = canonical
        return True

    def _bound_reference(self, address):
        participant = re.fullmatch(
            r"\$([A-Za-z_]\w*)(\.[A-Za-z_][A-Za-z_0-9. ]*)?", address
        )
        if participant and self.bindings.get(participant[1], "").startswith(
            "union:"
        ):
            suffix = participant[2] or ""
            branches = self.bindings[participant[1]][len("union:") :].split(
                "|"
            )
            return all(
                branch + suffix in self.exact_addresses for branch in branches
            )
        normalized = self._normalize_reference(address)
        if normalized is None:
            return False
        if "$" not in normalized:
            try:
                exact = (
                    canonical_model_address(normalized) in self.exact_addresses
                )
            except ValueError:
                exact = False
            if exact:
                _validate_exact_qualifiers(normalized, self.declared)
                return True
        if ")/" in normalized:
            return self._qualified_binding(normalized)
        try:
            bound_target = self.bound_names.get(
                simple_model_address(normalized)
            )
        except ValueError:
            bound_target = None
        if bound_target is not None:
            _validate_exact_qualifiers(bound_target, self.declared)
        return None

    def validate_reference(self, address: str) -> bool:
        if any(
            re.search(
                r"(?<![A-Za-z0-9_])" + re.escape(var) + r"(?![A-Za-z0-9_])",
                address,
            )
            for var in self.generic
        ):
            raise ValueError(
                "generic endpoint is scoped to its Relation signature"
            )
        if self.address_bindings is not None:
            result = self._bound_reference(address)
            if result is not None:
                return result
        return resolve_model_claim_reference(
            address,
            self.declared,
            self.relation_names,
            self.bindings,
            self.bound_names if self.address_bindings is not None else None,
        )

    def validate_relation_endpoint(
        self, address: str, name: object, side: str
    ) -> bool:
        if (
            side == "target"
            and name == "IS_DECLARED_BY"
            and self.relation_declaration == "IS_DECLARED_BY"
            and name in self.relation_names
            and self.address_bindings is not None
        ):
            selection = _requirement_form_selection(
                address, self.exact_addresses
            )
            if selection is not None:
                variable, identity = selection
                if (
                    f"${variable}" in self.generic
                    or self.bindings.get(variable, identity) != identity
                ):
                    raise ValueError(f"inconsistent binding: ${variable}")
                self.bindings[variable] = identity
                return True
            if re.fullmatch(r"\$[A-Za-z_]\w*", address) and self.bindings.get(
                address[1:], ""
            ).startswith("union:"):
                return self.validate_reference(address)
        if (
            isinstance(address, str)
            and re.fullmatch(r"\$[A-Za-z_]\w*", address)
            and name == self.relation_declaration
            and name in self.relation_names
        ):
            if address in self.generic or address[1:] in self.bindings:
                raise ValueError(
                    "generic endpoint cannot shadow another participant"
                )
            self.generic.add(address)
            return True
        return self.validate_reference(address)
