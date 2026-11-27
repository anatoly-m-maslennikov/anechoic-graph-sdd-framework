"""Stage Project Spec carriers before the managed build."""

from pathlib import Path

import httpx2


def _stage_spec_rows(binding, inputs, database):
    if inputs.get("structure_issues"):
        raise ValueError(
            "Structure source ingestion failed: "
            + str(inputs["structure_issues"])
        )
    if (
        not isinstance(database, dict)
        or set(database) != {"socket", "instance_id"}
        or not all(
            isinstance(value, str) and value for value in database.values()
        )
    ):
        raise ValueError("Invalid Spec database")
    snapshot_id, result = _snapshot_rows(binding, inputs, database)
    if (
        not isinstance(snapshot_id, str)
        or not snapshot_id
        or result["snapshot_id"] != snapshot_id
        or not isinstance(result["rows"], list)
    ):
        raise ValueError("Invalid Spec snapshot response")
    rows = result["rows"]
    by_path = {row["source_path"]: row for row in rows}
    control = Path(binding["control_root"])
    model_rows = []
    for old in inputs["rows"]:
        row = by_path[(control / old["source_path"]).as_posix()]
        model_rows.append(
            {
                key: old[key] if key == "source_path" else row[key]
                for key in ("source_path", "exact_ref", "metadata", "body")
            }
        )
    return {
        **inputs,
        "rows": model_rows,
        "spec_rows": rows,
        "snapshot_id": snapshot_id,
    }


def _snapshot_rows(binding, inputs, database):
    try:
        with httpx2.Client(
            transport=httpx2.HTTPTransport(uds=database["socket"]),
            base_url="http://private",
            timeout=125,
            trust_env=False,
        ) as client:
            response = client.put(
                "/spec-snapshot",
                json={
                    "instance_id": database["instance_id"],
                    "manifest_sha256": binding["manifest_sha256"],
                    "rows": inputs["spec_rows"],
                },
            )
            response.raise_for_status()
            snapshot_id = response.json()["result"]["snapshot_id"]
            response = client.get(
                "/spec-snapshot",
                params={
                    "instance_id": database["instance_id"],
                    "snapshot_id": snapshot_id,
                },
            )
            response.raise_for_status()
            result = response.json()["result"]
    except httpx2.HTTPError as error:
        raise ValueError(
            f"Spec snapshot database request failed: {error}"
        ) from error
    return snapshot_id, result
