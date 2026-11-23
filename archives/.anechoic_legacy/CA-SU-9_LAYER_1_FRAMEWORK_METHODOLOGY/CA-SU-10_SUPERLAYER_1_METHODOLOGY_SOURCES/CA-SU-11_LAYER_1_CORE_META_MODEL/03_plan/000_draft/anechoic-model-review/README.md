# Anechoic model review

Approved handoff from CA-P-3074 to CA-P-3075. CA-P-3089 records the approval
and verification. The handoff carries CA-C-745 and CA-C-746 forward.
CA-A-1466 proposes the Atom Header, exact references, and filename formula.
CA-R-3168 through CA-R-3203 hold the governing Drafts. CA-R-3169 records
the upstream-only import rule for ordered siblings discussed in CA-C-745.
CA-A-1466 records the SPEC, TKT, and PMETA carrier directories, including
the Backlog and PMETA status paths decided in CA-C-746.
It also records placement for linked and standalone Ticket assets.
CA-R-3171 records the single native Project Manifest and its identity fields.

The two native Claim files are the generation inputs. The generated
`anechoic_model.py` is a build output. The Python checks exercise the candidate
against the shared ANECHOIC generator and validators in isolation.

From the Project root, run:

```sh
packet="$(find .anechoic_anechoic -type d -path '*/03_plan/000_draft/anechoic-model-review' -print -quit)"
shasum -a 256 -c "$packet/SHA256SUMS" || exit
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
for check in verify_native_graph verify_native_templates verify_carrier_model structure_cases lens_cases import_cases io_cases lifecycle_cases carrier_cases; do
    .venv/bin/python "$packet/$check.py" || exit
done
```

Local Release excludes the Draft directory. The Apply Model Epic, CA-P-3075,
owns the migration and its Local Release checks.
