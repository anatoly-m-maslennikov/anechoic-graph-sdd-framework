"""Compile an ingested Model and retain its last admitted generation on failure."""
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model, open_serialized_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import mark_startup_timing, native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project
from .active_model_sources import _collect_active_source
from .compiler import write_model_records
from .structure_compile import compile_structure
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import _check_relation_references


class ModelRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    source_path: str
    exact_ref: str
    metadata: dict
    body: str


class ModelInputs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    rows: list[ModelRow]
    has_c9: bool
    issues: list[dict]
    accepted_model: dict | None


def _records(inputs):
    records, identifiers, subjects, seen = [], set(), set(), set()
    control = Path('/snapshot')
    custom_found = False
    for row in inputs.rows:
        path = PurePosixPath(row.source_path)
        parts = path.parts
        is_c9 = len(parts) in (2, 3) and parts[0] == 'LAYER_1_META_ONTOLOGY_C9' and (len(parts) == 2 or parts[1] in {'_SPEC', '_DES'})
        custom = len(parts) == 3 and parts[0] in {'__PROJECT_CONFIG', '002_PROJECT_CONFIG', 'PROJECT_CONFIG'} and parts[1] == 'CUSTOM_MODEL'
        if path.is_absolute() or str(path) != row.source_path or '..' in parts or '\\' in row.source_path or row.source_path in seen or not (is_c9 or custom):
            raise ValueError(f'{row.source_path}: invalid or duplicate Model source path')
        seen.add(row.source_path)
        header = native_header_view(row.metadata)
        identity, state = header.get('identity'), header.get('state')
        if not isinstance(identity, dict) or not isinstance(state, dict) or row.exact_ref != f'{identity.get("atom_id")}@{state.get("version")}':
            raise ValueError(f'{row.source_path}: exact reference disagrees with carrier')
        custom_found |= custom
        try:
            _collect_active_source(control / row.source_path, custom, None, control, identifiers, subjects, records, carrier=row)
        except (ValueError, TypeError, KeyError, SyntaxError) as error:
            error.source_path, error.atom_ref = row.source_path, row.exact_ref
            raise
    if not inputs.has_c9:
        if custom_found:
            raise ValueError('Custom Model sources require an active C9 Model')
        return None
    if not records:
        raise ValueError('No active Model Claims were selected')
    _check_relation_references(records)
    return tuple(records)


def _restore(directory, accepted):
    if accepted is None:
        write_model_records(directory, None)
        return
    with open_serialized_model(accepted):
        pass
    package = directory / 'anechoic_runtime_model'
    package.mkdir()
    for name, source in accepted['module_sources'].items():
        (package / name).write_text(source, encoding='utf-8')
    (directory / 'model.json').write_text(json.dumps(accepted, sort_keys=True), encoding='utf-8')


def _stage(directory, inputs, diagnostics, fallback=None):
    try:
        if fallback is not None:
            raise ValueError(str(fallback))
        if inputs.issues:
            raise ValueError('Model source ingestion failed: ' + json.dumps(inputs.issues, default=str))
        write_model_records(directory, _records(inputs))
    except (ValueError, TypeError, KeyError, SyntaxError) as error:
        attempt = uuid4().hex
        for issue in inputs.issues if inputs.issues and fallback is None else [{}]:
            diagnostics.append({'attempt_id': attempt, 'accepted_generation': None, 'severity': 'ERROR',
                                'code': issue.get('code') or 'invalid_model_source',
                                'message': issue.get('message') or str(error), 'atom_ref': issue.get('atom_ref') or getattr(error, 'atom_ref', None),
                                'source_path': issue.get('relative_path') or getattr(error, 'source_path', None), 'subject': None})
        for child in directory.iterdir():
            shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
        _restore(directory, inputs.accepted_model)
    digest = _serialize(directory)
    mark_startup_timing("model_ready", mode="reused" if diagnostics and inputs.accepted_model is not None else "built")
    return digest


def _serialize(directory):
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


def _structure(args, digest):
    descriptor = json.loads((args.generation / 'model.json').read_bytes())
    with open_admitted_model(args.generation, descriptor['model_sha256'], digest) as model:
        selection = resolve_native_project(args.project_root, args.control_root, validate_manifest=model.validate_manifest,
                                           require_atom_state=model.requires_atom_state,
                                           require_atom_header=model.requires_atom_header)
        if selection.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError('Project Manifest changed. Restart to apply its settings.')
        return compile_structure(selection, model)


def compile_ingested(args, raw):
    diagnostics = []
    try:
        inputs = ModelInputs.model_validate(raw)
        if (args.generation.is_symlink() or not args.generation.is_dir()
                or args.generation.resolve(strict=True) != args.generation or any(args.generation.iterdir())):
            raise ValueError('Model generation must be an empty canonical directory')
        digest = _stage(args.generation, inputs, diagnostics)
        try:
            snapshot = _structure(args, digest)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            if diagnostics:
                raise
            digest = _stage(args.generation, inputs, diagnostics, fallback=error)
            snapshot = _structure(args, digest)
        mark_startup_timing("structure_ready", mode="built")
        return {'structure': snapshot, 'model_descriptor_sha256': digest, 'model_diagnostics': diagnostics}
    except (OSError, RuntimeError, TypeError, ValueError, SyntaxError) as error:
        return {'error': {'code': 'model_compile_failed', 'message': str(error)}, 'model_diagnostics': diagnostics}


def compile_ingested_cli(args):
    try:
        result = compile_ingested(args, json.load(sys.stdin))
    except (OSError, ValueError, TypeError) as error:
        result = {'error': {'code': 'model_compile_failed', 'message': str(error)}, 'model_diagnostics': []}
    print(json.dumps(result, separators=(',', ':'), sort_keys=True),
          file=sys.stderr if 'error' in result else sys.stdout)
    if 'error' in result:
        raise SystemExit(1)
