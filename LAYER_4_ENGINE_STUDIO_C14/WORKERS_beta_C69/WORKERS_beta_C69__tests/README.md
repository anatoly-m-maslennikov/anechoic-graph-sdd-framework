# Beta generation profiler

Use this opt-in diagnostic for the current Beta Worker. Run from the repository root with the Engine environment:

```sh
PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/.venv/bin/python -B -m WORKERS_beta_C69.WORKERS_beta_C69__tests.generation.profile_generation --project-root /absolute/path/to/project
```

Add `--foreground` to profile the foreground generation with deferred Archive. Project selection uses the existing reviewed Model admission process. An existing native Worker binding JSON may instead be supplied with `--binding`.

The printed directory is under the selected Project's `.anechoic_tmp/beta-profile`. `report.json` contains stage wall time, Worker-process CPU time, source identity, and snapshot counts. `generation/` holds generated artifacts; the transient snapshot is counted and not retained. Failures leave `failure.txt`, the report when generation began, and child stderr.

`worker.pstats` profiles Worker-process Python CPU. The Manifest and Realization Graph each have separate Python CPU `.pstats` files. Their `*-children.json` files record subprocess wall times, including Node jobs. Child CPU is not included in Worker CPU. Profiling changes timings; do not use these measurements as unprofiled latency results.

The older Workbench `profile_workbench.py` measures the legacy SourceReader and QueryStore. Use it only for that path.
