"""Plain Journal read and append test cases."""

import copy
import json
from pathlib import Path


def read_records(directory: Path) -> list[object]:
    def order(path: Path) -> tuple[str, int]:
        partition, _, part = path.stem.rpartition("-part-")
        return partition, int(part) if partition and part.isdecimal() else 0

    return [
        record
        for path in sorted(directory.glob("*.ndjson"), key=order)
        for record in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
    ]


class PlainJournalCases:
    def test_append_and_read_preserve_input_order_and_content(self) -> None:
        rows = [
            {"custom": "first\nline", "nested": ["Ω", {"value": 7}]},
            {"custom": "second"},
        ]
        original = copy.deepcopy(rows)
        locations = self.append(rows)
        self.assertEqual(rows, read_records(self.directory))
        self.assertEqual(original, rows)
        self.assertEqual([1, 2], [row["line"] for row in locations])
        self.assertEqual([None, None], [row["event_id"] for row in locations])

    def test_later_append_extends_stored_rows_in_order(self) -> None:
        first, second = [{"value": 1}], [{"value": 2}, {"value": 3}]
        self.append(first)
        self.append(second)
        self.assertEqual(first + second, read_records(self.directory))
