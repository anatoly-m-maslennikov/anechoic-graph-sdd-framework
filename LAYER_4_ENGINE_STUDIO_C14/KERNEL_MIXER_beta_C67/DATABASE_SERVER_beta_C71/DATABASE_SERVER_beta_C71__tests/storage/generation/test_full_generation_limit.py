"""Check request limits on the live generation routes."""

import unittest

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


def padded_body(size):
    yield b"{}"
    block = b" " * (1024 * 1024)
    remaining = size - 2
    while remaining:
        chunk = block[: min(remaining, len(block))]
        yield chunk
        remaining -= len(chunk)


class FullGenerationLimitTest(unittest.TestCase):
    def test_limits_preserve_previous_generation(self):
        with _server() as client:
            response = client.put("/generation", json=_generation())
            self.assertEqual(200, response.status_code, response.text)
            before = _query(client, "SELECT * FROM mrt_atoms").json()[
                "result"
            ]["rows"]
            for path, size, message in (
                (
                    "/generation/native",
                    64 * 1024 * 1024 + 1,
                    "Invalid request fields",
                ),
                (
                    "/generation/native-delta",
                    64 * 1024 * 1024 + 1,
                    "Request is too large",
                ),
                ("/generation", 128 * 1024 * 1024 + 1, "Request is too large"),
            ):
                with self.subTest(path=path):
                    response = client.put(
                        path, content=padded_body(size), timeout=60
                    )
                    self.assertEqual(400, response.status_code, response.text)
                    self.assertIn(message, response.text)
                    self.assertEqual(
                        before,
                        _query(client, "SELECT * FROM mrt_atoms").json()[
                            "result"
                        ]["rows"],
                    )
            self.assertEqual(
                200, client.get("/structure", params=BINDING).status_code
            )
