"""Declared Role folders drive Workbench filename audits."""
from pathlib import Path
import tempfile
import unittest


from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _declared_filename_issue
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import DeclarationSource, compile_content_schema
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import filename_role_matches
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import (
    compile_role_folders, compile_schema, load_image_schema, schema_asset,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_structured_python_model_claim


class RoleFolderTests(unittest.TestCase):
    def test_filename_role_is_taken_before_the_slug(self):
        for name in ("CA-C-526-runtime-draft.md", "12-TEAM-PROJECT-C-527-follows-CA-P-1.md"):
            with self.subTest(name=name):
                self.assertTrue(filename_role_matches(Path("01_concern") / name))
                self.assertFalse(filename_role_matches(Path("03_plan") / name))

    def test_formal_folders_round_trip_and_control_audit(self):
        analysis = parse_native_model_claim('''
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Analysis and Advisory", qualification_property_path="Atom.Header.Context.Role",
               classifications={"Role Order Number": 2})
''')
        plan, = parse_structured_python_model_claim('''
classify(address="Atom/(.Header.Context.Role := Plan)", axis="Role Order Number", value=3, grouped=True)
''')
        source = DeclarationSource('CA-R-2637', 1, 'role.md')
        declared = compile_role_folders([(analysis, source), (plan, source)])
        folders = tuple(sorted((role, value[0]) for role, value in declared.items()))
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / 'schema.json'
            asset.write_bytes(schema_asset([], compile_schema([], compile_content_schema([]), role_folders=folders)))
            folders = load_image_schema(asset).role_folders
        self.assertTrue(filename_role_matches(Path('02_analysis_and_advisory/CA-A-1-record.md'), folders))
        self.assertFalse(filename_role_matches(Path('02_analysis_and_advisory/CA-P-1-record.md'), folders))
        self.assertFalse(filename_role_matches(Path('03_plan/02_analysis_and_advisory/CA-P-1-record.md'), folders))
        self.assertTrue(filename_role_matches(Path('02_analysis/CA-P-1-record.md'), folders))
        self.assertFalse(filename_role_matches(Path('02_analysis/CA-P-1-record.md')))
        issue = _declared_filename_issue('CA-P-1-record.md', '02_analysis_and_advisory', {'id': 'CA-P-1', 'role': 'Plan'}, folders)
        self.assertEqual('file.name', issue[0])


if __name__ == '__main__':
    unittest.main()
