"""In-memory HTTP connection for restart checkpoint cases."""

import json


def _reuse_connection(reuse, calls):
    class Connection:
        def __init__(self, path):
            pass

        def request(self, method, path):
            calls.append((method, path))

        def getresponse(self):
            class Response:
                status = 200

                def read(self):
                    return json.dumps({"result": reuse}).encode()

            return Response()

        def close(self):
            pass

    return Connection
