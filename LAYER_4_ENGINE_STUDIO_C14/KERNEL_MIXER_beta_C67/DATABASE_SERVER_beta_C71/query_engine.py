"""Open a DuckDB connection with the runtime's installed query extension."""

import os

import duckdb


def connect(database):
    config = {"memory_limit": "256MB", "temp_directory": "",
              "autoinstall_known_extensions": False, "autoload_known_extensions": False}
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
