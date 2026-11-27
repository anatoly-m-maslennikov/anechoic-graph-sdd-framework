"""Open a DuckDB connection with the runtime's installed query extension."""

import os

import duckdb


def connect(database):
    config = {
        "memory_limit": "256MB",
        "autoinstall_known_extensions": False,
        "autoload_known_extensions": False,
    }
    if database == ":memory:":
        config["temp_directory"] = ""
    else:
        config["max_temp_directory_size"] = "512MB"
    extensions = os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY")
    if extensions:
        config["extension_directory"] = extensions
    connection = duckdb.connect(database, config=config)
    try:
        connection.execute("LOAD duckpgq")
        connection.execute("SET active_grammar_extensions = ['duckpgq']")
    except BaseException:
        connection.close()
        raise
    return connection
