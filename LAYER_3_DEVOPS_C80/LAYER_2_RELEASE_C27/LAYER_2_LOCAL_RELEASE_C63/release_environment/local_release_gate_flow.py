"""Assemble and execute the Local Release test-gate request."""


def _gate_arguments(values, gate, cwd, phase, engine, source_bound):
    argv = gate._gate_command(cwd, phase, engine, source_bound)
    if phase == "functional" and values["functional_fast"]:
        argv += ("--functional-suite", "fast")
    if (
        phase in {"image", "image-tests", "canary"}
        and values["functional_fast"]
    ):
        argv += ("--image-suite", "fast")
    if phase in {"image", "image-tests", "canary"}:
        if values["candidate_image"] is None:
            raise gate.LocalReleaseError(
                "local-release-candidate-image-invalid"
            )
        argv += ("--candidate-image", values["candidate_image"])
        values["verify"](values["package"], values["package_identity"])
    if phase in {"image", "canary"}:
        argv += gate._canary_arguments(
            cwd,
            values["package"],
            values["selection"],
            values["run_id"],
            values["canary_root"],
            values["canary_settings_sha256"],
        )
    return argv


def _gate_result(values, gate, phase, log_phase, result):
    if getattr(result, "returncode", 1) != 0:
        detail = values["failed_output"](
            values["root"],
            values["run_id"],
            result,
            log_path=values["log_paths"].get(log_phase),
        )
        if phase == "preflight":
            detail = f"{detail}\n{gate._PREFLIGHT_SETUP}"
        raise gate.LocalReleaseError(f"local-release-command-failed: {detail}")
    if phase in {"image", "canary"}:
        return gate._canary_endpoint(result.stdout)
    return None


def run_gate_flow(values, gate):
    root = values["root"]
    cwd = values["source_root"] or root
    source_bound = values["source_bound"] or values["source_root"] is not None
    engine = (
        cwd if source_bound else gate._ROOT
    ) / "LAYER_4_ENGINE_STUDIO_C14"
    phase = values["suite_phase"]
    log_phase = "image" if phase == "image-tests" else phase
    if (
        values["source_root"] is not None
        and values["runner"] is None
        and phase in {"image-tests", "canary"}
    ):
        phase = gate._source_image_phase(cwd, phase, engine)
    argv = _gate_arguments(values, gate, cwd, phase, engine, source_bound)
    result = gate._run_gate_command(
        root,
        cwd,
        values["run_id"],
        log_phase,
        argv,
        values["runner"],
        values["log_paths"],
        engine=engine,
        target=values["target"],
        named_file=values["named_file"],
        logged_process=values["logged_process"],
        log_directory=values["log_directory"],
        record_logs=values["record_logs"],
    )
    return _gate_result(values, gate, phase, log_phase, result)
