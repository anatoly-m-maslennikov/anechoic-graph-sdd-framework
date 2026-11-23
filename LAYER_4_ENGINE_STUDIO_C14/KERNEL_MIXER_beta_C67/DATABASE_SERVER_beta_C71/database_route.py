"""Run or page a query for the Project bound to this database."""

from itertools import combinations

import duckdb
from starlette.responses import JSONResponse

from .result_delivery import database_result
from .saved_query_runs import save_run_fields, validate_run_save


_DELIVERY = ("grid", "result_delivery", "result_format", "preview")


def _variants(required, optional):
    return tuple(required.union(keys) for count in range(len(optional) + 1)
                 for keys in combinations(optional, count))


_FIELDS = ({"instance_id", "sql"},
           *_variants({"instance_id", "sql", "page_size"}, _DELIVERY + ("save", "name")),
           *_variants({"instance_id", "query_id", "offset", "page_size"}, _DELIVERY))


def database_route(connection, instance_id, lock, queries, journal_sync, project_root, saved_queries, read_object, error):
    async def database(request):
        try:
            data = await read_object(request, 65536, *_FIELDS)
            if data["instance_id"] != instance_id:
                return error("foreign_instance", "Instance does not match", 403)
            save = validate_run_save(data)
            with lock:
                if connection.execute("SELECT id FROM generation").fetchone() is None:
                    return error("generation_required", "Generation admission required", 409)
                if journal_sync is not None and "sql" in data:
                    journal_sync()
                result = database_result(connection, queries, data, project_root)
                if save:
                    result.update(save_run_fields(saved_queries, data["sql"], data.get("name")))
            return JSONResponse({"result": result})
        except (ValueError, TypeError, duckdb.Error) as exc:
            return error("invalid_query", str(exc), 400)
        except (OSError, RuntimeError):
            return error("journal_unavailable", "Work Journal is unavailable", 409)

    return database
