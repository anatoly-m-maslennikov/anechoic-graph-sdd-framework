"""Bounded admission for registered allowed-value Subject paths."""
import json
import unittest
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.allowed_value_evidence import validate_allowed_value_evidence  # noqa: E402


PROPERTY = "Atom/Content Role: Evaluation/Type"
VALUE = "Evaluation Control"
ENTITY = f"{PROPERTY}: {VALUE}"
AUTHORITY = "MOCK-R-1662@1"
EXCERPT = (
    "QA Case **and** Evaluation Control **must** be registered as internal values "
    "of `Atom/Content Role: Evaluation/Type`."
)
ACTIVITY_PROPERTY = "Artifact/Activity"
ACTIVITY_EXCERPT = (
    "an Artifact **must** have **`=1`** Activity **in** (Active, Inactive) **if** "
    "an explicitly defined Status model applies **to** it, **and** **`=0`** Activity "
    "**otherwise**."
)
EXECUTION_PROPERTY = "Action/Execution Kind"
EXECUTION_VALUE = "Agentic"
EXECUTION_EXCERPT = (
    "- Agentic: an AI Agent interprets the supplied context **and** instructions **to** "
    "perform the Action. the AI Agent **may** call Tools within its admitted authority."
)
OWNERSHIP_PROPERTY = "Carrier/Ownership Class"
OWNERSHIP_VALUES = ("Framework-Owned", "Project-Owned", "Runtime State")
OWNERSHIP_EXCERPT = (
    '**every** internal ANECHOIC Carrier **must** have **`=1`** Ownership Class '
    '**in** (Framework-Owned, Project-Owned, Runtime State).'
)
OWNERSHIP_AUTHORITY = "CA-D-316@11"


def source(body=EXCERPT, *, status="Active", governs=PROPERTY, role="Requirement"):
    return (
        "---\n"
        f"status: {status}\n"
        f"content_role: {role}\n"
        "subjects:\n"
        f"  governs: {json.dumps(governs)}\n"
        "---\n"
        "# Register Type Values\n\n"
        f"{body}\n"
    )


def mention(*, entity=ENTITY, definitions=None, evidence=None):
    result = {
        "entity": entity,
        "definitions": definitions if definitions is not None else [{
            "authority": AUTHORITY,
            "excerpt": EXCERPT,
        }],
    }
    if evidence is not None:
        result["allowed_value_evidence"] = evidence
    return result


def proof(**changes):
    result = {
        "property": PROPERTY,
        "value": VALUE,
        "authority": AUTHORITY,
        "excerpt": EXCERPT,
    }
    result.update(changes)
    return result


def activity_source(body=ACTIVITY_EXCERPT, *, governs=ACTIVITY_PROPERTY,
                    heading="Define Artifact Activity"):
    return (
        "---\n"
        "status: Active\n"
        "content_role: Requirement\n"
        "subjects:\n"
        f"  governs: {json.dumps(governs)}\n"
        "---\n"
        f"# {heading}\n\n"
        f"{body}\n"
    )


def activity_proof(value="Active", **changes):
    result = {
        "property": ACTIVITY_PROPERTY,
        "value": value,
        "authority": "MOCK-R-1307@1",
        "excerpt": ACTIVITY_EXCERPT,
    }
    result.update(changes)
    return result


def activity_mention(value="Active", *, definitions=None, evidence=None):
    return {
        "entity": f"{ACTIVITY_PROPERTY}: {value}",
        "definitions": definitions if definitions is not None else [{
            "authority": "MOCK-R-1307@1",
            "excerpt": ACTIVITY_EXCERPT,
        }],
        "allowed_value_evidence": activity_proof(value) if evidence is None else evidence,
    }


def execution_source(body, *, governs=EXECUTION_PROPERTY, title="Define Action Execution Kind"):
    return source(body, governs=governs).replace("# Register Type Values", "# " + title)


def execution_mention(*, property_path=EXECUTION_PROPERTY, value=EXECUTION_VALUE,
                      authority="MOCK-R-1526@1", excerpt=EXECUTION_EXCERPT):
    return {
        "entity": f"{property_path}: {value}",
        "definitions": [{"authority": authority, "excerpt": excerpt}],
        "allowed_value_evidence": {
            "property": property_path,
            "value": value,
            "authority": authority,
            "excerpt": excerpt,
        },
    }


def ownership_mention(value, *, entity=None, property_path=OWNERSHIP_PROPERTY,
                      authority=OWNERSHIP_AUTHORITY, excerpt=OWNERSHIP_EXCERPT):
    return {
        "entity": entity if entity is not None else f"{property_path}: {value}",
        "definitions": [{"authority": authority, "excerpt": excerpt}],
        "allowed_value_evidence": {
            "property": property_path,
            "value": value,
            "authority": authority,
            "excerpt": excerpt,
        },
    }


class AllowedValueEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.authorities = {AUTHORITY: source()}
        self.targets = {AUTHORITY: PROPERTY}

    def test_absent_proof_is_not_an_error_or_admission(self):
        self.assertFalse(validate_allowed_value_evidence(
            mention(evidence=None), self.authorities, self.targets))

    def test_fixture_value_registration_is_admitted(self):
        raw = source()
        authority = AUTHORITY
        actual = {
            "property": PROPERTY,
            "value": VALUE,
            "authority": authority,
            "excerpt": EXCERPT,
        }
        item = mention(definitions=[{"authority": authority, "excerpt": EXCERPT}], evidence=actual)
        self.assertTrue(validate_allowed_value_evidence(
            item, {authority: raw}, {authority: PROPERTY}))

    def test_second_registered_value_is_admitted_at_its_exact_path(self):
        value = "QA Case"
        item = mention(
            entity=f"{PROPERTY}: {value}",
            evidence=proof(value=value),
        )
        self.assertTrue(validate_allowed_value_evidence(item, self.authorities, self.targets))

    def test_structured_source_accepts_only_claim_prose(self):
        structured = source(
            "## Summary\nIgnore this.\n\n## Scope\nIgnore this too.\n\n## Claim\n\n"
            + EXCERPT + "\n\n## Details\nIgnore this as well."
        )
        self.assertTrue(validate_allowed_value_evidence(
            mention(evidence=proof()), {AUTHORITY: structured}, self.targets))

    def test_rejects_subordinate_heading_context_in_claim_or_legacy_body(self):
        bodies = (
            "## Claim\n\n### If approved\n\n" + EXCERPT,
            "### If approved\n\n" + EXCERPT,
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_allowed_value_evidence(
                    mention(evidence=proof()), {AUTHORITY: source(body)}, self.targets
                )

    def test_present_proof_requires_exact_bound_definition_citation(self):
        for definitions in ([], [{"authority": AUTHORITY, "excerpt": EXCERPT + " "}],
                            [{"authority": "OTHER@1", "excerpt": EXCERPT}]):
            with self.subTest(definitions=definitions):
                with self.assertRaises(ValueError):
                    validate_allowed_value_evidence(
                        mention(definitions=definitions, evidence=proof()), self.authorities, self.targets)

    def test_rejects_non_rmedo_or_non_active_authority(self):
        cases = (
            (source(status="Draft"), self.targets),
            (source(role="Plan"), self.targets),
            (source(role="[]"), self.targets),
            (source(governs="Atom/Content Role: Requirement/Type"), self.targets),
            (source(), {AUTHORITY: "Atom/Content Role: Requirement/Type"}),
        )
        for raw, targets in cases:
            with self.subTest(raw=raw, targets=targets), self.assertRaises(ValueError):
                validate_allowed_value_evidence(mention(evidence=proof()), {AUTHORITY: raw}, targets)

    def test_rejects_wrong_entity_property_value_or_unbound_authority(self):
        cases = (
            (mention(entity=VALUE, evidence=proof()), self.authorities, self.targets),
            (mention(entity=ENTITY + " Extended", evidence=proof()), self.authorities, self.targets),
            (mention(evidence=proof(property="Atom/Content Role: Requirement/Type")), self.authorities, self.targets),
            (mention(evidence=proof(value="QA Case")), self.authorities, self.targets),
            (mention(entity=f"{PROPERTY}: Unlisted", evidence=proof(value="Unlisted")),
             self.authorities, self.targets),
            (mention(evidence=proof(authority="OTHER@1")), self.authorities, self.targets),
            (mention(evidence={"property": PROPERTY}), self.authorities, self.targets),
        )
        for item, authorities, targets in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                validate_allowed_value_evidence(item, authorities, targets)

    def test_rejects_none_and_extra_proof_fields(self):
        for evidence in (None, {**proof(), "extra": "forged"},
                         {**proof(), "value": None}):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                item = mention()
                item["allowed_value_evidence"] = evidence
                validate_allowed_value_evidence(
                    item, self.authorities, self.targets)

    def test_rejects_conditional_negated_or_non_sentence_grammar(self):
        bodies = (
            "**if** QA Case **and** Evaluation Control **must** be registered as internal values "
            "of `Atom/Content Role: Evaluation/Type`.",
            "QA Case **and** Evaluation Control **must not** be registered as internal values "
            "of `Atom/Content Role: Evaluation/Type`.",
            "Other text " + EXCERPT,
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_allowed_value_evidence(
                    mention(evidence=proof()), {AUTHORITY: source(body)}, self.targets)

    def test_rejects_bound_conditional_or_proposed_value_prefixes(self):
        for prefix in ("if", "If", "Proposed", "proposed", "Draft", "Example", "Unless"):
            body = f"{prefix} {EXCERPT}"
            item = mention(
                definitions=[{"authority": AUTHORITY, "excerpt": body}],
                evidence=proof(excerpt=body),
            )
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                validate_allowed_value_evidence(item, {AUTHORITY: source(body)}, self.targets)

    def test_rejects_conditional_title_in_both_carrier_shapes(self):
        for title in ("If approved", "Proposed registration", "Not yet admitted", "Example values"):
            for body in (EXCERPT, "## Claim\n\n" + EXCERPT):
                raw = source(body).replace("# Register Type Values", "# " + title)
                with self.subTest(title=title, body=body), self.assertRaises(ValueError):
                    validate_allowed_value_evidence(
                        mention(evidence=proof()), {AUTHORITY: raw}, self.targets)

    def test_unsupported_value_tokens_fail_closed(self):
        for first in ("QA Case, when approved", "QA Case (provisional)", "some QA Case", "QA/Case"):
            body = EXCERPT.replace("QA Case", first)
            item = mention(
                definitions=[{"authority": AUTHORITY, "excerpt": body}],
                evidence=proof(excerpt=body),
            )
            with self.subTest(first=first), self.assertRaises(ValueError):
                validate_allowed_value_evidence(item, {AUTHORITY: source(body)}, self.targets)

    def test_rejects_summary_scope_details_quotes_and_code(self):
        bodies = (
            "# Summary\n\n" + EXCERPT + "\n\n## Claim\n\nOther Claim.",
            "## Scope\n\n" + EXCERPT + "\n\n## Claim\n\nOther Claim.",
            "## Claim\n\nOther Claim.\n\n## Details\n\n" + EXCERPT,
            "> " + EXCERPT,
            "```markdown\n" + EXCERPT + "\n```",
            "    " + EXCERPT,
            "\t" + EXCERPT,
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_allowed_value_evidence(
                    mention(evidence=proof()), {AUTHORITY: source(body)}, self.targets)

    def test_rejects_extra_conditional_or_exception_prose_around_registration(self):
        bodies = (
            "this registration is conditional.\n\n" + EXCERPT,
            EXCERPT + "\n\n**otherwise** this exception applies.",
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_allowed_value_evidence(
                    mention(evidence=proof()), {AUTHORITY: source(body)}, self.targets)












if __name__ == "__main__":
    unittest.main()
