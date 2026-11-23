# Content declaration schema fixtures

These fixtures preserve the historic inputs used by the content declaration schema tests.
The 391 carriers in `04_requirement` are byte-for-byte copies from
`.anechoic_legacy/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement`.
The tests combine them with 270 byte-identical carriers in the sealed
`FEATURE_TOOLS__tests/assets/lifecycle_schema_declarations/04_requirement` fixture.
Together they reproduce the original 661 carriers (896,555 bytes).

`content_declaration_schema__shared.py` and its pattern helper derive from the historical script in
`.anechoic_legacy/02_analysis_and_advisory/000_draft/header-groups-20261106/references`.
They preserve the prepared Header-group transformation used by the golden comparison.
`residual-review.json` preserves the historical review input.
