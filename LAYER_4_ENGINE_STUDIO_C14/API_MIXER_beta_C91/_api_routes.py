"""Build Tool and Worker Run request handlers."""

import json


def tool_route(
    api,
    instance,
    project_root,
    host_root,
    tools,
    blacklist,
    readiness,
    database,
    jobs,
    worker_binding,
    project_name,
    workbench_public_url,
):
    async def invoke(request):
        return await _invoke(
            api,
            request,
            instance,
            project_root,
            host_root,
            tools,
            blacklist,
            readiness,
            database,
            jobs,
            worker_binding,
            project_name,
            workbench_public_url,
        )

    return invoke


async def _invoke(
    api,
    request,
    instance,
    project_root,
    host_root,
    tools,
    blacklist,
    readiness,
    database,
    jobs,
    worker_binding,
    project_name,
    workbench_public_url,
):
    data = await _parse(api, request, instance, project_root, host_root)
    if isinstance(data, api.JSONResponse):
        return data
    if data.name not in tools or data.name in blacklist:
        return api.JSONResponse(
            api.failure("tool_unavailable", "Unknown Tool")
        )
    if problem := readiness.guard():
        return api.refusal(
            {
                "state": "unavailable"
                if problem["error"]["code"] == "admission_gate_unavailable"
                else "pending",
                **problem,
            }
        )
    if data.name not in api.PROJECTION_TOOLS and not readiness.admitted:
        status = await readiness.status()
        if status["state"] != "ready":
            return api.refusal(status)
    return await api._invoke_direct(
        data,
        database,
        jobs,
        worker_binding,
        instance,
        project_name,
        workbench_public_url,
    )


async def _parse(api, request, instance, project_root, host_root):
    try:
        data = api.ToolRequest.model_validate(
            json.loads(await api.body(request))
        )
        if data.instance_id != instance:
            raise ValueError("Invalid Tool request envelope")
        if data.asserted_project_root not in (
            None,
            project_root,
            host_root,
        ):
            raise ValueError("project_root does not match the bound Project")
    except (ValueError, TypeError, api.ValidationError) as error:
        return api.JSONResponse(api.failure("value_error", str(error)))
    return data


def worker_runs_route(api, jobs, instance):
    async def worker_runs(request):
        if list(request.query_params.multi_items()) != [
            ("instance_id", instance)
        ]:
            return api.JSONResponse(
                api.failure(
                    "value_error", "Invalid Worker Run request binding"
                )
            )
        try:
            result = await api.peer(
                jobs,
                "GET",
                "/jobs/worker-runs",
                params={"instance_id": instance},
            )
            api.WorkerRuns.model_validate(result["result"])
            return api.JSONResponse(result)
        except api.httpx2.HTTPError, ValueError, TypeError, KeyError:
            return api.JSONResponse(
                api.failure(
                    "workbench_unavailable", "Orchestrator unavailable"
                ),
                status_code=503,
            )

    return worker_runs
