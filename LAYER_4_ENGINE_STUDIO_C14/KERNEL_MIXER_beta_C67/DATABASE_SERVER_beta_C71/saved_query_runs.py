"Validate save options and keep a completed run pageable after save failure."

import duckdb


def validate_name(name):
    if not isinstance(name, str):
        raise ValueError("name must be a string")
    name.encode("utf-8")


def validate_run_save(arguments):
    save = arguments.get("save", False)
    if type(save) is not bool:
        raise ValueError("save must be a boolean")
    if "name" in arguments:
        if not save:
            raise ValueError("name is only supported when save is true")
        validate_name(arguments["name"])
    return save


def save_sql(saved_queries, sql, kind, name):
    if saved_queries is None:
        raise OSError("Saved SQL storage is unavailable")
    return saved_queries.save(sql, kind, name)


def save_run_fields(saved_queries, sql, name):
    try:
        record = save_sql(saved_queries, sql, "query", name)
    except (OSError, RuntimeError, ValueError, duckdb.Error) as error:
        return {
            "outcome": "partial",
            "save_error": str(error) or "Saved SQL storage is unavailable",
        }
    return {"saved_query_id": record["saved_query_id"]}
