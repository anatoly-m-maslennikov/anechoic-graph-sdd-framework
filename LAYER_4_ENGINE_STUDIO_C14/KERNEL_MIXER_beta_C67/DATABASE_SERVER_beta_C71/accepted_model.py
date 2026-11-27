"""Keep the accepted executable Model in one private Project asset."""

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
from uuid import uuid4


from .work_journal import _open_directory

_DIRECTORY = ('.anechoic_runtime', 'assets')
_NAME = 'generated_model.json'
_HEX = re.compile(r'[0-9a-f]{64}\Z')


def _validate(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Model key')
            result[key] = value
        return result
    doc = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(doc, dict):
        raise ValueError('Invalid accepted Model')
    hashes, sources = doc.get('modules'), doc.get('module_sources')
    if (not isinstance(hashes, dict) or not isinstance(sources, dict)
            or '__init__.py' not in hashes or set(hashes) != set(sources)):
        raise ValueError('Invalid accepted Model modules')
    for name, digest in hashes.items():
        source = sources[name]
        if (not isinstance(name, str) or not name.endswith('.py') or not name[:-3].isidentifier()
                or not isinstance(digest, str) or _HEX.fullmatch(digest) is None
                or not isinstance(source, str) or sha256(source.encode()).hexdigest() != digest
                or (name == '__init__.py' and source)):
            raise ValueError('Invalid accepted Model module integrity')
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.model_generation__pub import _validate_binding_descriptor
    _validate_binding_descriptor(doc, hashes)
    return raw


def _read(root):
    try:
        directory = _open_directory(root, _DIRECTORY, create=False, same_device=True)
    except FileNotFoundError:
        return None
    try:
        try:
            fd = os.open(_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        except FileNotFoundError:
            return None
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ValueError('Accepted Model file is unavailable or unsafe')
            return stream.read()
    finally:
        os.close(directory)


def initialize(connection, root):
    root = str(Path(root))
    connection.execute('CREATE TEMP TABLE accepted_model_state (root VARCHAR, model VARCHAR, reason VARCHAR)')
    read_failed = False
    reason = 'Accepted Model asset is missing'
    try:
        raw = _read(Path(root))
        model = _validate(raw.decode('utf-8')) if raw is not None else None
        if model is not None:
            reason = 'Accepted Model asset has no generation receipt'
    except (ValueError, UnicodeError, OSError):
        model = None
        read_failed = True
        reason = 'Accepted Model asset is invalid or unsafe'
    row = connection.execute('SELECT model FROM ops_generation').fetchone()
    if row:
        stored = row[0]
        valid_receipt = False
        if isinstance(stored, str) and _HEX.fullmatch(stored) is None:
            try:
                _validate(stored)
                if model is None and not read_failed:
                    pending = _prepare_file(Path(root), stored)
                    _publish_file(pending)
                    model = stored
                if model == stored:
                    connection.execute('UPDATE ops_generation SET model = ?', [sha256(stored.encode()).hexdigest()])
                    valid_receipt = True
            except (ValueError, UnicodeError):
                pass
        elif model is not None and sha256(model.encode()).hexdigest() == stored:
            valid_receipt = True
        if not valid_receipt:
            if model is not None:
                reason = 'Accepted Model asset does not match its generation receipt'
            connection.execute('DELETE FROM ops_generation')
    if not row or not valid_receipt:
        model = None
    connection.execute('INSERT INTO accepted_model_state VALUES (?, ?, ?)', [root, model, reason])
    connection.execute('''CREATE OR REPLACE TEMP VIEW int_lifecycle_generation AS
        SELECT g.id, accepted.model, g.structure
        FROM main.ops_generation g
        JOIN temp.main.accepted_model_state accepted ON g.model = sha256(accepted.model)''')


def managed(connection):
    exists = connection.execute("SELECT count(*) FROM duckdb_tables() WHERE database_name = 'temp' "
                                "AND schema_name = 'main' AND table_name = 'accepted_model_state'").fetchone()[0]
    return connection.execute('SELECT root, model, reason FROM temp.main.accepted_model_state').fetchone() if exists else None


def model_value(connection, stored):
    state = managed(connection)
    return state[1] if state else stored


def generation_rows(connection):
    rows = connection.execute('SELECT id, model, structure FROM ops_generation').fetchall()
    return [(row[0], model_value(connection, row[1]), row[2]) for row in rows]


def _prepare_file(root, model):
    directory = _open_directory(root, _DIRECTORY, create=True, same_device=True)
    temporary = f'.{uuid4().hex}.tmp'
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(model)
            stream.flush()
            os.fsync(stream.fileno())
        return directory, temporary
    except BaseException:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
        os.close(directory)
        raise


def _publish_file(pending):
    directory, temporary = pending
    try:
        os.replace(temporary, _NAME, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
        os.close(directory)


def discard(pending):
    if pending:
        directory, temporary = pending
        try:
            os.unlink(temporary, dir_fd=directory)
        finally:
            os.close(directory)


def prepare(connection, model):
    state = managed(connection)
    if not state:
        return model, None
    _validate(model)
    root = Path(state[0])
    raw = model.encode('utf-8')
    unchanged = state[1] is not None and raw == _read(root)
    return sha256(raw).hexdigest(), None if unchanged else _prepare_file(root, model)


def publish(connection, model, pending):
    update = 'UPDATE accepted_model_state SET model = ?'
    try:
        state = managed(connection)
        if not state:
            return
        if pending is None and model.encode('utf-8') != _read(Path(state[0])):
            pending = _prepare_file(Path(state[0]), model)
        connection.execute(update, [model])
    except BaseException:
        try:
            discard(pending)
        finally:
            connection.execute('DELETE FROM ops_generation')
        raise
    if pending:
        try:
            _publish_file(pending)
        except BaseException:
            connection.execute('DELETE FROM ops_generation')
            connection.execute(update, [state[1]])
            raise
