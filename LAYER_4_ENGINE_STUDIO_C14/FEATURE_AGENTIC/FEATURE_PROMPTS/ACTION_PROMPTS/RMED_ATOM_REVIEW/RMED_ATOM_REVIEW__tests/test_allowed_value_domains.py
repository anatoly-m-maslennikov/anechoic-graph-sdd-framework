"""Allowed-value evidence for named and conditional domains."""
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.test_allowed_value_evidence import (
    ACTIVITY_EXCERPT,
    ACTIVITY_PROPERTY,
    AUTHORITY,
    EXECUTION_EXCERPT,
    EXECUTION_PROPERTY,
    OWNERSHIP_AUTHORITY,
    OWNERSHIP_EXCERPT,
    OWNERSHIP_PROPERTY,
    OWNERSHIP_VALUES,
    PROPERTY,
    activity_mention,
    activity_proof,
    activity_source,
    execution_mention,
    execution_source,
    ownership_mention,
    source,
)

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.allowed_value_evidence import validate_allowed_value_evidence



class AllowedValueDomainEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.authorities = {AUTHORITY: source()}
        self.targets = {AUTHORITY: PROPERTY}


    def test_fixture_agentic_named_value_bullet_is_admitted(self):
        raw = execution_source("Action Execution Kind **means** one selected execution form.\n\n" + EXECUTION_EXCERPT)
        authority = "MOCK-R-1526@1"
        self.assertTrue(validate_allowed_value_evidence(
            execution_mention(authority=authority), {authority: raw},
            {authority: EXECUTION_PROPERTY}))


    def test_named_value_bullet_rejects_unknown_non_governing_wrong_property_and_cropping(self):
        opening = "Action Execution Kind **means** one selected execution form."
        raw = execution_source(opening + "\n\n" + EXECUTION_EXCERPT)
        authority = "MOCK-R-1526@1"
        cases = (
            (execution_mention(value="Unknown"), raw, {authority: EXECUTION_PROPERTY}),
            (execution_mention(), raw, {authority: "Action"}),
            (execution_mention(property_path="Action/Kind"), raw, {authority: EXECUTION_PROPERTY}),
            (execution_mention(excerpt="- Agentic: an AI Agent interprets the supplied context"), raw,
             {authority: EXECUTION_PROPERTY}),
        )
        for item, evidence_raw, targets in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                validate_allowed_value_evidence(item, {authority: evidence_raw}, targets)


    def test_named_value_bullet_rejects_conditional_example_negated_and_non_list_context(self):
        opening = "Action Execution Kind **means** one selected execution form."
        cases = (
            "- Agentic: an AI Agent performs the Action **if** approved.",
            "- Agentic: Example execution by an AI Agent performs the Action.",
            "- Agentic: an AI Agent does **not** perform the Action.",
            "Agentic: an AI Agent performs the Action.",
        )
        authority = "MOCK-R-1526@1"
        for bullet in cases:
            raw = execution_source(opening + "\n\n" + bullet)
            item = execution_mention(excerpt=bullet)
            with self.subTest(bullet=bullet), self.assertRaises(ValueError):
                validate_allowed_value_evidence(item, {authority: raw}, {authority: EXECUTION_PROPERTY})


    def test_fixture_conditional_domain_admits_both_activity_values(self):
        raw = activity_source()
        authority = "MOCK-R-1307@1"
        targets = {authority: ACTIVITY_PROPERTY}
        for value in ("Active", "Inactive"):
            with self.subTest(value=value):
                item = activity_mention(
                    value,
                    definitions=[{"authority": authority, "excerpt": ACTIVITY_EXCERPT}],
                    evidence=activity_proof(value, authority=authority),
                )
                self.assertTrue(validate_allowed_value_evidence(item, {authority: raw}, targets))


    def test_conditional_domain_rejects_wrong_path_value_or_sentence_shape(self):
        authority = "MOCK-R-1307@1"
        targets = {authority: ACTIVITY_PROPERTY}
        malformed = (
            (ACTIVITY_EXCERPT.replace("an Artifact", "an Record"), ACTIVITY_PROPERTY, "Active"),
            (ACTIVITY_EXCERPT, "Artifact/Revision/Status", "Active"),
            (ACTIVITY_EXCERPT, ACTIVITY_PROPERTY, "Unknown"),
            (ACTIVITY_EXCERPT.replace("**`=1`**", "**`>=1`**"), ACTIVITY_PROPERTY, "Active"),
            (ACTIVITY_EXCERPT.replace("**`=0`** Activity", "**`=0`** Status"), ACTIVITY_PROPERTY, "Active"),
            (ACTIVITY_EXCERPT.replace(", **and** **`=0`** Activity **otherwise**", ""), ACTIVITY_PROPERTY, "Active"),
        )
        for body, property_path, value in malformed:
            with self.subTest(body=body, property_path=property_path, value=value):
                evidence = activity_proof(property=property_path, value=value, excerpt=body)
                item = activity_mention(
                    value,
                    definitions=[{"authority": authority, "excerpt": body}],
                    evidence=evidence,
                )
                with self.assertRaises(ValueError):
                    validate_allowed_value_evidence(
                        item, {authority: activity_source(body)}, targets)


    def test_conditional_domain_rejects_context_and_non_domain_classification(self):
        authority = "MOCK-R-1307@1"
        cases = (
            activity_source(heading="Proposed Artifact Activity"),
            activity_source(heading="If approved"),
            activity_source(ACTIVITY_EXCERPT + "\n\nAdditional context."),
            activity_source("> " + ACTIVITY_EXCERPT),
            activity_source("```markdown\n" + ACTIVITY_EXCERPT + "\n```"),
            activity_source().replace("status: Active\n", "status: Active\nstatus: Draft\n"),
        )
        item = activity_mention()
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    validate_allowed_value_evidence(
                        item, {authority: raw}, {authority: ACTIVITY_PROPERTY})

        classification = (
            "the Artifact Property Activity **means** the derived Property that classifies "
            "an Artifact as Active **or** Inactive from its current Revision Status within "
            "the applicability defined by CA-R-1307."
        )
        raw = activity_source(classification, heading="Define Artifact Activity")
        only_classification = activity_mention(
            definitions=[{"authority": "CA-R-1394@10", "excerpt": classification}],
            evidence=activity_proof(authority="CA-R-1394@10", excerpt=classification),
        )
        with self.assertRaises(ValueError):
            validate_allowed_value_evidence(
                only_classification, {"CA-R-1394@10": raw},
                {"CA-R-1394@10": ACTIVITY_PROPERTY})


    def test_conditional_domain_rejects_dependent_only_authority(self):
        authority = "MOCK-R-OTHER@1"
        raw = activity_source(governs="Artifact/Revision/Status").replace(
            "  governs: \"Artifact/Revision/Status\"\n",
            "  governs: \"Artifact/Revision/Status\"\n"
            "  depends_on:\n"
            "    - \"Artifact/Activity\"\n",
        )
        item = activity_mention(
            definitions=[{"authority": authority, "excerpt": ACTIVITY_EXCERPT}],
            evidence=activity_proof(authority=authority),
        )
        with self.assertRaises(ValueError):
            validate_allowed_value_evidence(
                item, {authority: raw}, {authority: "Artifact/Revision/Status"})


    def test_conditional_domain_accepts_another_direct_exact_domain(self):
        authority = "MOCK-R-DISPOSITION@1"
        property_path = "Record/Disposition"
        excerpt = (
            "an Record **must** have **`=1`** Disposition **in** (Kept, Discarded) "
            "**if** an explicitly defined Status model applies **to** it, **and** "
            "**`=0`** Disposition **otherwise**."
        )
        raw = activity_source(
            excerpt, governs=property_path, heading="Define Record Disposition")
        for value in ("Kept", "Discarded"):
            with self.subTest(value=value):
                evidence = {
                    "property": property_path,
                    "value": value,
                    "authority": authority,
                    "excerpt": excerpt,
                }
                item = {
                    "entity": f"{property_path}: {value}",
                    "definitions": [{"authority": authority, "excerpt": excerpt}],
                    "allowed_value_evidence": evidence,
                }
                self.assertTrue(validate_allowed_value_evidence(
                    item, {authority: raw}, {authority: property_path}))


    def test_conditional_domain_rejects_wrong_proof_bearer_or_authority_target(self):
        authority = "MOCK-R-DISPOSITION@1"
        property_path = "Record/Disposition"
        excerpt = (
            "an Record **must** have **`=1`** Disposition **in** (Kept, Discarded) "
            "**if** an explicitly defined Status model applies **to** it, **and** "
            "**`=0`** Disposition **otherwise**."
        )
        raw = activity_source(
            excerpt, governs=property_path, heading="Define Record Disposition")

        wrong_bearer = {
            "property": "Artifact/Disposition",
            "value": "Kept",
            "authority": authority,
            "excerpt": excerpt,
        }
        wrong_bearer_item = {
            "entity": "Artifact/Disposition: Kept",
            "definitions": [{"authority": authority, "excerpt": excerpt}],
            "allowed_value_evidence": wrong_bearer,
        }
        with self.assertRaises(ValueError):
            validate_allowed_value_evidence(
                wrong_bearer_item, {authority: raw}, {authority: property_path})

        correct_proof_wrong_target = {
            "property": property_path,
            "value": "Kept",
            "authority": authority,
            "excerpt": excerpt,
        }
        correct_item = {
            "entity": "Record/Disposition: Kept",
            "definitions": [{"authority": authority, "excerpt": excerpt}],
            "allowed_value_evidence": correct_proof_wrong_target,
        }
        with self.assertRaises(ValueError):
            validate_allowed_value_evidence(
                correct_item, {authority: raw}, {authority: "Record/Status"})


    def test_fixture_internal_carrier_ownership_domain_is_bounded(self):
        raw = source(OWNERSHIP_EXCERPT, governs=OWNERSHIP_PROPERTY, role="Delivery")
        claim_with_extra = raw.replace(
            OWNERSHIP_EXCERPT, OWNERSHIP_EXCERPT + "\nExtra context.")
        targets = {OWNERSHIP_AUTHORITY: OWNERSHIP_PROPERTY}
        for value in OWNERSHIP_VALUES:
            with self.subTest(value=value):
                self.assertTrue(validate_allowed_value_evidence(
                    ownership_mention(value), {OWNERSHIP_AUTHORITY: raw}, targets))

        rejected = (
            (ownership_mention("Framework-Owned", entity="Framework-Owned Carrier"), raw, targets),
            (ownership_mention("Framework-Owned", property_path="Artifact/Ownership Class"), raw, targets),
            (ownership_mention("External-Owned"), raw, targets),
            (ownership_mention("Framework-Owned"), claim_with_extra, targets),
            (ownership_mention(
                "Framework-Owned",
                excerpt=OWNERSHIP_EXCERPT.replace("internal ANECHOIC ", ""),
            ), raw.replace("internal ANECHOIC ", ""), targets),
            (ownership_mention("Framework-Owned"), raw.replace("status: Active", "status: Draft"), targets),
            (ownership_mention("Framework-Owned"), raw, {OWNERSHIP_AUTHORITY: "Other/Ownership Class"}),
        )
        for item, evidence_raw, evidence_targets in rejected:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    validate_allowed_value_evidence(
                        item, {OWNERSHIP_AUTHORITY: evidence_raw}, evidence_targets)


