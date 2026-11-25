import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR import native_manifest_model as native


class MigratedCallbackPinsTests(unittest.TestCase):
    def test_previous_seed_callback_still_binds(self):
        records = native.reviewed_model_records()[0]
        previous = [
            (source, subject, native._previous_seed_claim(claim) if subject == native._SEED_SUBJECT else claim)
            for source, subject, claim in records
        ]
        model = native._NativeModel(records=previous)
        seed = model.validate_component_seed_manifest({
            "atom_id": "AN-S-125", "ref_id": "AN-S-125@1", "version": 1, "tier": 2,
            "component_seed_id": "CS123", "purpose": "Purpose", "solution": "Solution",
        }, "C01")
        self.assertEqual(seed.solution, "Solution")

    def test_component_seed_manifest_pin_uses_manifest_scope(self):
        old = native._OLD_ATOM + '//Spec Atom//Component Seed Manifest'
        target = native._NEW_ATOM + '//Specification//Manifest//Component Seed Manifest'
        self.assertEqual(native._CHECK_TARGET_MIGRATION[old], target)
        records = native.reviewed_model_records()[0]
        index = next(i for i, (_, subject, _) in enumerate(records)
                     if subject == 'MODEL//ANECHOIC <+ ' + old)
        source, _, claim = records[index]
        with patch.object(native, '_check_relation_references'):
            for path, accepted in ((old, True), (target, True),
                                   (native._NEW_ATOM + '//Specification//Component Seed Manifest', False)):
                candidate = [*records[:index], (source, 'MODEL//ANECHOIC <+ ' + path, claim), *records[index + 1:]]
                with self.subTest(path=path):
                    if accepted:
                        native.admit_active_model_records(candidate)
                    else:
                        with self.assertRaisesRegex(ValueError, 'instance check differs'):
                            native.admit_active_model_records(candidate)

    def test_reviewed_callback_is_bound_to_exact_old_or_agreed_new_target(self):
        records = native.reviewed_model_records()[0]
        index = next(i for i, (_, _, claim) in enumerate(records) if 'def check_atom_identity(' in claim)
        source, subject, claim = records[index]
        relocated = subject.replace(native._OLD_ATOM, native._NEW_ATOM)
        with patch.object(native, '_check_relation_references'):
            native.admit_active_model_records([*records[:index], (source, relocated, claim), *records[index + 1:]])
            for changed_subject, changed_claim in (
                (relocated.replace('/Content/Atom', '/Other/Atom'), claim),
                (relocated, claim.replace('len(parts) != 3', 'len(parts) != 4')),
                (relocated, claim.replace('check_atom_identity', 'check_other_identity')),
                (relocated, claim.replace('class Atom(', 'class OtherAtom(').replace('entity_class=Atom', 'entity_class=OtherAtom')),
            ):
                with self.subTest(subject=changed_subject, claim=changed_claim[-100:]):
                    with self.assertRaises(ValueError):
                        native.admit_active_model_records([*records[:index], (source, changed_subject, changed_claim), *records[index + 1:]])
            with self.assertRaisesRegex(ValueError, 'instance check differs'):
                native.admit_active_model_records([*records, (source + 'other', relocated, claim)])

    def test_all_six_agreed_callback_targets_are_admitted_together(self):
        records = native.reviewed_model_records()[0]
        migrated = []
        changed = 0
        for source, subject, claim in records:
            if 'instance_check=' in claim:
                for old, new in native._CHECK_TARGET_MIGRATION.items():
                    if subject == 'MODEL//ANECHOIC <+ ' + old:
                        subject = 'MODEL//ANECHOIC <+ ' + new
                        changed += 1
                        break
            migrated.append((source, subject, claim))
        self.assertEqual(6, changed)
        with patch.object(native, '_check_relation_references'):
            native.admit_active_model_records(migrated)
