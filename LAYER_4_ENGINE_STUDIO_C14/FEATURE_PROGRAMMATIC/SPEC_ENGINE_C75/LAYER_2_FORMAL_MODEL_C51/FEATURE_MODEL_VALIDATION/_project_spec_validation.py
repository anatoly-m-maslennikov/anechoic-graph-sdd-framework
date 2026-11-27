"""Validate project SPECs against the bound Model."""

from types import SimpleNamespace


def project_spec_template(self, template, effective_relation_constraints):
    if template in {"task", "epic"}:
        return None
    legacy = {
        "project_contract": ("Project Contract", 0),
        "axiom": ("Axiom", 0),
        "applicable_principle": ("Applicable Principle", 2),
    }
    candidates = []
    for name, display, cls, enabled in self._declared_types:
        fixed = self.fixed_property_value(name, "template")
        if fixed != template and not (
            template in legacy
            and display == legacy[template][0]
            and fixed is None
        ):
            continue
        if not issubclass(cls, self._types["Spec Atom"]):
            continue
        relation = effective_relation_constraints(cls, self._bindings).get(
            self._containment_relation, {}
        )
        targets = relation.get("target_entity_paths", ())
        if not any(
            self._types.get(target) is self._types["Project"]
            for target in targets
        ):
            continue
        tier = self.fixed_property_value(name, "tier")
        if tier is None:
            field = cls.__dataclass_fields__.get("tier")
            default = field.default if field is not None else None
            tier = (
                default
                if type(default) is int
                else legacy.get(template, (None, None))[1]
            )
        candidates.append((name, tier, enabled))
    if len(candidates) > 1:
        raise ValueError(
            "Project SPEC template is ambiguous in the compiled Model"
        )
    return candidates[0] if candidates else None


def validate_project_spec(
    self, template, header, owner_id, body, summary_fields
):
    view, fields = _project_spec_fields(self, header)
    resolved = self.project_spec_template(template)
    if resolved is None:
        raise ValueError(
            "Project SPEC template is not supported by the compiled Model"
        )
    name, _, _ = resolved
    if (
        owner_id != "C00"
        or view["context"].get("container") != {"component": "C00"}
        or view["context"].get("template") != template
        or type(fields.get("tier")) is not int
    ):
        raise ValueError(
            "Project SPEC requires Project C00 and its declared Tier"
        )
    if self.declares_summary(name) and isinstance(body, str):
        fields.update(summary_fields(body))
    if self.declares_property(name, "guarantee"):
        fields["guarantee"] = _guarantee(body)
    project = self._validate("Project", {}, {})
    return self._validate(
        name, fields, {self._containment_relation: [project]}
    )


def _guarantee(body):
    from markdown_it import MarkdownIt

    if not isinstance(body, str):
        raise ValueError("Project Contract requires Guarantee prose")
    tokens = MarkdownIt("commonmark").parse(body)
    headings = [
        i
        for i, token in enumerate(tokens)
        if token.type == "heading_open"
        and token.tag == "h2"
        and token.level == 0
        and tokens[i + 1].content.strip() == "Guarantee"
    ]
    if len(headings) != 1:
        raise ValueError("Project Contract requires one Guarantee")
    start = headings[0]
    end = next(
        (
            i
            for i in range(start + 1, len(tokens))
            if tokens[i].type == "heading_open"
            and tokens[i].level == 0
            and tokens[i].tag in {"h1", "h2"}
        ),
        len(tokens),
    )
    section = tokens[start + 1 : end]
    if not any(
        t.type == "inline"
        and t.content.strip()
        and i
        and section[i - 1].type == "paragraph_open"
        for i, t in enumerate(section)
    ):
        raise ValueError("Project Contract requires Guarantee prose")
    lines = body.splitlines()
    end_line = tokens[end].map[0] if end < len(tokens) else len(lines)
    guarantee = "\n".join(lines[tokens[start].map[1] : end_line]).strip()
    return guarantee


def _project_spec_fields(self, header):
    from ....FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import (
        derive_atom_ref,
    )
    from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        manifest_state_fields,
        native_header_view,
    )

    view = native_header_view(header)
    state = view["state"]
    atom_id = view["identity"]["atom_id"]
    fields = {
        "atom_id": atom_id,
        "version": state["version"],
        "ref_id": derive_atom_ref(atom_id, state["version"], state["status"]),
        "tier": view["context"].get("tier"),
        "lens": view["context"].get("lens"),
    }
    if self.requires_atom_state:
        fields.update(
            manifest_state_fields(
                SimpleNamespace(metadata=header),
                include_header=self.requires_atom_header,
            )
        )
    return view, fields
