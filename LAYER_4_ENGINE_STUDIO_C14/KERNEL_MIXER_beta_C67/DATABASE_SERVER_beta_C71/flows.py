"""Project observed flows and admit bounded, causal runtime snapshots."""

import json
import math
import re
import sys

import duckdb
from starlette.responses import JSONResponse

_RUN = re.compile(r"[0-9a-f]{32}\Z")
_COMPONENT = re.compile(r"C(?:S)?[0-9]+\Z")
_FIELDS = {"kind", "name", "at", "causes", "target", "outcome", "detail"}


def initialize_flows(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS src_flow_events (
        run_id VARCHAR NOT NULL, component VARCHAR NOT NULL, action VARCHAR NOT NULL,
        sequence INTEGER NOT NULL, kind VARCHAR NOT NULL, name VARCHAR NOT NULL,
        "at" DOUBLE NOT NULL, causes INTEGER[] NOT NULL, target VARCHAR, outcome VARCHAR,
        detail JSON NOT NULL, PRIMARY KEY (run_id, sequence))""")
    connection.execute("""CREATE OR REPLACE VIEW mrt_flow_overlap_candidates AS
        SELECT component, action, list_sort(list(DISTINCT name)) AS trigger_names,
          count(DISTINCT run_id) AS run_count
        FROM src_flow_events WHERE kind = 'trigger' GROUP BY component, action
        HAVING count(DISTINCT name) >= 2""")
    connection.execute("""CREATE OR REPLACE VIEW mrt_flow_similar_actions AS
        WITH traces AS (
            SELECT component, action, run_id,
                list(struct_pack(kind := kind, name := name, target := target) ORDER BY sequence) AS shape
            FROM src_flow_events WHERE kind IN ('output', 'effect') GROUP BY component, action, run_id
            HAVING bool_or(kind = 'output') AND NOT bool_or(
                json_exists(detail, '$.omitted_events') OR json_exists(detail, '$.unattributed'))
        ), action_shapes AS (
            SELECT component, action, shape, min(run_id) AS example_run, count(*) AS run_count
            FROM traces GROUP BY component, action, shape
        )
        SELECT to_json(shape) AS observable_shape,
            list(struct_pack(component := component, action := action, example_run := example_run,
                             run_count := run_count) ORDER BY component, action) AS actions
        FROM action_shapes GROUP BY shape HAVING count(*) > 1""")
    _initialize_flow_actions(connection)


def _initialize_flow_actions(connection):
    connection.execute("""CREATE OR REPLACE VIEW mrt_flow_actions AS
        WITH by_trigger AS (
            SELECT t.component, t.action, t.name,
                coalesce(list(DISTINCT i.name ORDER BY i.name)
                         FILTER (WHERE i.name IS NOT NULL), []) AS inputs
            FROM src_flow_events t
            LEFT JOIN src_flow_events i ON i.run_id = t.run_id AND i.kind = 'input'
                AND list_contains(t.causes, i.sequence)
            WHERE t.kind = 'trigger'
            GROUP BY t.component, t.action, t.name
        ), trigger_maps AS (
            SELECT component, action, json_group_object(name, inputs) AS triggers
            FROM by_trigger GROUP BY component, action
        ), observations AS (
            SELECT component, action,
                arg_max(json_extract(detail, '$.unit'), "at" ORDER BY run_id DESC, sequence DESC)
                    FILTER (WHERE kind = 'trigger') AS unit,
                to_json(coalesce(list(DISTINCT name ORDER BY name)
                    FILTER (WHERE kind = 'input'), [])) AS inputs,
                to_json(coalesce(list(DISTINCT name ORDER BY name)
                    FILTER (WHERE kind = 'output'), [])) AS outputs,
                to_json(coalesce(list(DISTINCT name ORDER BY name)
                    FILTER (WHERE kind = 'effect'), [])) AS effects
            FROM src_flow_events GROUP BY component, action
        )
        SELECT component, action, json_extract_string(unit, '$.path') AS unit_path,
            json_extract_string(unit, '$.name') AS unit_name,
            inputs, coalesce(triggers, '{}'::JSON) AS triggers, outputs, effects
        FROM observations LEFT JOIN trigger_maps USING (component, action)""")


def _validate(data):
    if (not isinstance(data['run_id'], str) or not _RUN.fullmatch(data['run_id'])
            or not isinstance(data['component'], str) or not _COMPONENT.fullmatch(data['component'])
            or not isinstance(data['action'], str) or not data['action'].strip()
            or not isinstance(data['events'], list) or len(data['events']) > 512):
        raise ValueError('Invalid flow snapshot')
    rows = []
    for sequence, event in enumerate(data['events']):
        if not isinstance(event, dict) or set(event) != _FIELDS:
            raise ValueError('Invalid event fields')
        at, causes = event['at'], event['causes']
        if (event['kind'] not in ('input', 'trigger', 'output', 'effect')
                or not isinstance(event['name'], str)
                or isinstance(at, bool) or not isinstance(at, (int, float))
                or not math.isfinite(at) or at < 0
                or not isinstance(causes, list)
                or any(type(cause) is not int or cause < 0 or cause >= sequence for cause in causes)
                or any(event[key] is not None and not isinstance(event[key], str) for key in ('target', 'outcome'))
                or not isinstance(event['detail'], dict)):
            raise ValueError('Invalid event values or causes')
        detail = json.dumps(event['detail'], ensure_ascii=False, allow_nan=False)
        rows.append((data['run_id'], data['component'], data['action'], sequence,
                     event['kind'], event['name'], at, causes, event['target'], event['outcome'], detail))
    return rows


def flow_route(connection, instance_id, lock, read_object, error):
    async def admit(request):
        try:
            data = await read_object(request, 1024 * 1024,
                                     {'instance_id', 'run_id', 'component', 'action', 'events'})
            if data['instance_id'] != instance_id:
                print('Flow events rejected: instance does not match', file=sys.stderr)
                return error('foreign_instance', 'Instance does not match', 403)
            rows = _validate(data)
            with lock:
                connection.execute('BEGIN TRANSACTION')
                try:
                    if rows:
                        connection.executemany('INSERT INTO src_flow_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', rows)
                    connection.execute('COMMIT')
                except BaseException:
                    connection.execute('ROLLBACK')
                    raise
            return JSONResponse({'result': {'run_id': data['run_id'], 'events': len(rows)}})
        except (ValueError, TypeError, OverflowError, UnicodeError, duckdb.Error) as exc:
            print(f'Flow events rejected: {exc}', file=sys.stderr)
            return error('invalid_flow_events', str(exc), 400)
    return admit
