"""Stage an ingested Model candidate and retain the admitted fallback on failure."""
from hashlib import sha256
import json
import shutil
from uuid import uuid4

import duckdb

from .compiler import build_model_from_rows
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model, open_serialized_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import is_ontology_model_source


def select_model_rows(rows):
    with duckdb.connect(':memory:') as db:
        db.execute('CREATE TABLE source (source_path VARCHAR, exact_ref VARCHAR, metadata JSON, body VARCHAR, status VARCHAR, is_ontology BOOLEAN)')
        for row in rows:
            status = native_header_view(row['metadata']).get('state', {}).get('status')
            db.execute('INSERT INTO source VALUES (?, ?, ?, ?, ?, ?)',
                       [row['source_path'], row['exact_ref'], json.dumps(row['metadata'], default=str), row['body'], status, is_ontology_model_source(row['source_path'])])
        selected = db.execute("""SELECT source_path, exact_ref, metadata, body FROM source
            WHERE status = 'active' AND (
              is_ontology OR
              regexp_full_match(source_path, '(__PROJECT_CONFIG|002_PROJECT_CONFIG|PROJECT_CONFIG)/CUSTOM_MODEL/[^/]+'))
            ORDER BY source_path""").fetchall()
    return [dict(source_path=path, exact_ref=ref, metadata=json.loads(metadata), body=body)
            for path, ref, metadata, body in selected]


def stage_model(directory, inputs, accepted, diagnostics, *, fallback=None):
    if (not isinstance(inputs, dict) or set(inputs) != {'rows', 'has_c9', 'issues', 'accepted_model'}
            or not isinstance(inputs['rows'], list) or type(inputs['has_c9']) is not bool
            or not isinstance(inputs['issues'], list)
            or any(not isinstance(issue, dict) for issue in inputs['issues'])
            or (inputs['accepted_model'] is not None and not isinstance(inputs['accepted_model'], dict))):
        raise ValueError('Invalid Model snapshot envelope')
    attempt = uuid4().hex
    try:
        if fallback is not None:
            raise ValueError(str(fallback))
        if inputs['issues']:
            raise ValueError('Model source ingestion failed: ' + json.dumps(inputs['issues'], default=str))
        rows = select_model_rows(inputs['rows'])
        build_model_from_rows(directory, rows, has_c9=inputs['has_c9'])
    except (ValueError, TypeError, KeyError, SyntaxError) as error:
        issues = inputs['issues'] if inputs['issues'] and fallback is None else [None]
        for issue in issues:
            issue = issue or {}
            diagnostics.append({"attempt_id": attempt, "accepted_generation": None, "severity": "ERROR",
                                "code": issue.get("code") or getattr(error, "code", "model_candidate_invalid"),
                                "message": issue.get("message") or str(error),
                                "atom_ref": issue.get("atom_ref") or getattr(error, "atom_ref", None),
                                "source_path": issue.get("relative_path") or getattr(error, "source_path", None),
                                "subject": getattr(error, "subject", None)})
        for child in directory.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        if accepted is None:
            build_model_from_rows(directory, [], has_c9=False)
        else:
            with open_serialized_model(accepted):
                pass
            package = directory / 'anechoic_runtime_model'
            package.mkdir()
            for name, source in accepted['module_sources'].items():
                (package / name).write_text(source, encoding='utf-8')
            (directory / 'model.json').write_text(json.dumps(accepted, sort_keys=True), encoding='utf-8')
    return _serialize_model(directory)


def _serialize_model(directory):
    path = directory / 'model.json'
    raw = path.read_bytes()
    descriptor = json.loads(raw)
    with open_admitted_model(directory, descriptor['model_sha256'], sha256(raw).hexdigest()) as model:
        descriptor['ticket_labels'] = model.ticket_labels
    descriptor['module_sources'] = {name: (directory / 'anechoic_runtime_model' / name).read_text(encoding='utf-8')
                                    for name in descriptor['modules']}
    if any(sha256(source.encode('utf-8')).hexdigest() != descriptor['modules'][name]
           for name, source in descriptor['module_sources'].items()):
        raise ValueError('Model modules changed during serialization')
    path.write_text(json.dumps(descriptor, sort_keys=True), encoding='utf-8')
    return sha256(path.read_bytes()).hexdigest()
