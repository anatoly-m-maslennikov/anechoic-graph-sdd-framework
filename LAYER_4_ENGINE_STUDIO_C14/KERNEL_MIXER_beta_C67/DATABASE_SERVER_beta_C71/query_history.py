"""Mirror completed technical query attempts in the owning Kernel."""

import sys

from .query_log import QueryLog


class QueryHistory:
    def __init__(self, root, connection):
        self.log = QueryLog(root)
        self.connection = connection
        connection.execute(
            'CREATE TEMP TABLE query_log_records (log_id VARCHAR PRIMARY KEY, "at" TIMESTAMPTZ, sql VARCHAR, '
            'outcome VARCHAR, error VARCHAR, row_count BIGINT, column_count BIGINT)'
        )
        connection.execute(
            'CREATE TEMP VIEW query_log AS SELECT * FROM query_log_records '
            'WHERE "at" > current_timestamp - INTERVAL 48 HOURS'
        )
        try:
            self._mirror(self.log.load())
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def _mirror(self, records):
        if records:
            self.connection.execute('DELETE FROM temp.main.query_log_records '
                                    'WHERE "at" <= current_timestamp - INTERVAL 48 HOURS')
            self.connection.executemany(
                'INSERT OR REPLACE INTO temp.main.query_log_records VALUES (?, ?, ?, ?, ?, ?, ?)',
                [(row['log_id'], row['at'], row['sql'], row['outcome'], row['error'],
                  row['row_count'], row['column_count']) for row in records],
            )

    def sync(self):
        try:
            self._mirror(self.log.take_pending())
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def append(self, *args, **kwargs):
        try:
            self.log.append(*args, **kwargs)
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def invoke(self, operation, args):
        if operation == "query_log_list" and set(args) <= {"limit"}:
            return self.log.list(args.get("limit", 20))
        if operation == "query_log_get" and set(args) == {"log_id"}:
            return self.log.get(args["log_id"])
        raise ValueError("Invalid query log request")

    def close(self):
        self.log.close()
