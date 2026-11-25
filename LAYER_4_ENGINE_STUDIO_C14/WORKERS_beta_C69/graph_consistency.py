"""Read typed graph consistency evidence."""
import json


def _graph_consistency(stderr):
    try:
        record = json.loads(stderr[-4096:].rstrip().rsplit("\n", 1)[-1])
        if (record["code"] == "realization_graph_inputs_changed" and record["component"] == "C61"
                and record["severity"] == "ERROR" and isinstance(record["details"], dict)):
            return record["details"]
    except (ValueError, TypeError, KeyError):
        pass
    return None


