---
atom_family: SPEC
atom_id: AN-S-3337
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 35
  updated_at: "2026-11-28T15:16:37.698017+00:00"
---
## Summary

Declare Orchestrator Beta

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C68',
    name='Orchestrator Beta',
    lens_whitelist=['DES', 'SPEC', 'SWD/INTERNAL_API/IPC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['generation.generation__shared.DeltaRequiresReconciliation', 'generation.generation__shared.WorkerIngestionFailure', 'archive_operations.archive_operations__shared.ArchiveCoverageLost', 'archive_operations.archive_operations__shared.ArchiveInputsChanged', 'watching.poll_coverage.poll_coverage__shared.ArchiveCoverage', 'watching.poll_coverage.poll_coverage__shared.PollingProof', 'archive_operations.archive_jobs', 'archive_operations.archive_jobs.ARCHIVE_RECONCILIATION', 'archive_operations.archive_jobs.ArchiveCoverageLost', 'archive_operations.archive_jobs.ArchiveInputsChanged', 'archive_operations.archive_jobs.ArchiveJobs', 'archive_operations.archive_jobs._ARCHIVE_FENCE_MESSAGE', 'generation.worker.checkpoint.startup_checkpoint.archive_checkpoint', 'watching.poll_coverage.watcher_diagnostics.FOREGROUND_FENCE_MESSAGE', 'watching.poll_coverage.watcher_diagnostics.FenceDiagnostics', 'watching.poll_coverage.watcher_diagnostics.emit_record', 'watching.poll_coverage.watcher_diagnostics.report_fence_failure', 'watching.poll_coverage.watcher_diagnostics.report_graph_consistency', 'watching.poll_coverage.watcher_diagnostics.report_graph_restart', 'watching.poll_coverage.watcher_poll_coverage.ArchiveCoverage', 'watching.poll_coverage.watcher_poll_coverage.PollingProof', 'watching.watcher_poll',
                               'settings.container_settings__pub.CONTAINER_SETTINGS_FILENAME',
                               'settings.container_settings__pub.parse_container_settings',
                               'settings.settings_carrier__pub.parse_settings_carrier','model__shared.is_ontology_model_source', 'model__shared.ontology_component_path', 'project__shared.console_state_path', 'sources__shared.mark_startup_timing',
                               'ORCHESTRATOR_beta_C68__shared.admit_generation',
                               'ORCHESTRATOR_beta_C68__shared.confirm_reuse',
                               'ORCHESTRATOR_beta_C68__shared.read_reuse',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.Connection',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.ENGINE',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.Kernel',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.RunFixture',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.kernel_server',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.latest',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.lifecycle_job',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.project',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.project_jobs',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.request_json',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.restore_reuse',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.wait_for',
                               'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.watch_project',
                               'ORCHESTRATOR_beta_C68__tests.generation._worker_diagnostics_cases.WorkerDiagnosticsCases',
                               'ORCHESTRATOR_beta_C68__tests.lifecycle.test_lifecycle_queries.database',
                               'abort.WorkerAborted',
                               'generation.generation.CompilerColumnsChanged',
                               'generation.generation.DeltaRequiresReconciliation',
                               'generation.generation.GenerationBaseChanged',
                               'generation.generation.MAX_WARM_DELTA_PATHS',
                               'generation.generation.TICKET_ROOTS',
                               'generation.generation.WorkerIngestionFailure',
                               'generation.generation.admit_generation',
                               'generation.generation.confirm_reuse',
                               'generation.generation.live_reuse',
                               'generation.generation.parse_worker_result',
                               'generation.generation.read_accepted_model',
                               'generation.generation.read_reuse',
                               'generation.generation.read_structure',
                               'generation.generation.replace_ingestion_issues',
                               'generation.generation.ticket_delta_paths',
                               'generation.generation.wait_build',
                               'generation.generation.worker_failure',
                               'generation.generation.worker_request',
                               'generation.generation_flow.GenerationFlow',
                               'generation.generation_live_capture.GenerationLiveCapture',
                               'generation.generation_requests.GenerationRequests',
                               'generation.startup_graph.StartupGraphJobs',
                               'generation.worker.checkpoint.startup_checkpoint.CHECKPOINT_FIELDS',
                               'generation.worker.checkpoint.startup_checkpoint.MAX_DELTA_PATHS',
                               'generation.worker.checkpoint.startup_checkpoint.ReuseRecord',
                               'generation.worker.checkpoint.startup_checkpoint.checkpoint_paths',
                               'generation.worker.checkpoint.startup_checkpoint.compatible_checkpoint',
                               'generation.worker.flow.Flow',
                               'generation.worker.flow.safe_target',
                               'generation.worker.generation_worker.ForegroundCoverageLost',
                               'generation.worker.generation_worker.ForegroundInputsChanged',
                               'generation.worker.generation_worker.GENERATION_ERRORS',
                               'generation.worker.generation_worker.GenerationWorker',
                               'generation.worker.warm_worker.WarmLifecycleUnavailable',
                               'generation.worker.warm_worker.run_lifecycle',
                               'generation.worker.worker_reply.parse_graph_result',
                               'generation.worker.worker_reply.parse_worker_result',
                               'jobs.ENGINE',
                               'jobs.FIELDS',
                               'jobs.LifecycleCoveragePending',
                               'jobs.UnixConnection',
                               'jobs._GenerationJob',
                               'jobs._LifecycleJob',
                               'jobs._Run',
                               'jobs.operation_timeout',
                               'lifecycle.documents.atom_document.document',
                               'lifecycle.lifecycle.LifecycleJobs',
                               'lifecycle.lifecycle_queries.lifecycle_context',
                               'lifecycle.lifecycle_queries.lifecycle_sql',
                               'peers.project_admission.AdmissionClient',
                               'peers.project_admission._selection',
                               'peers.project_peers.ProjectBinding',
                               'peers.project_peers.open_project_peers',
                               'peers.project_peers.socket_path',
                               'peers.shared_host_config.load',
                               'peers.shared_project_pool.SharedProjectPool',
                               'peers.warm_worker_process.open_warm_worker',
                               'peers.warm_worker_process.process_environment',
                               'watching.retry.COVERAGE_RECOVERED',
                               'watching.retry.CurrentnessRetry',
                               'watching.retry.source_changed',
                               'watching.watcher.SourceWatcher',
                               'watching.watcher_poll.PollComplete','archive_jobs',
                               'metrics__shared.is_measurement_input',
                               'ADAPTERS_C30__shared.console_state_path',
                               'container_settings__pub.CONTAINER_SETTINGS_FILENAME',
                               'container_settings__pub.parse_container_settings',
                               'settings_carrier__pub.parse_settings_carrier',
                               'ADAPTERS_C30__shared.CEILINGS',
                               'ADAPTERS_C30__shared.ReadContext',
                               'ADAPTERS_C30__shared.native_carrier_path',
                               'ADAPTERS_C30__shared.native_header_view',
                               'ADAPTERS_C30__shared.parse_carrier',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.is_ontology_model_source',
                               'ADAPTERS_C30__shared.ontology_component_path',
                               'ATOM_LIFECYCLE__shared.ticket_status_options',
                               'ADAPTERS_C30__shared.mark_startup_timing',
                               'ORCHESTRATOR_beta_C68__shared',
                               'ORCHESTRATOR_beta_C68__shared.Flow',
                               'ORCHESTRATOR_beta_C68__shared.GenerationJobs',
                               'lifecycle_queries.lifecycle_context',
                               'lifecycle_queries.lifecycle_sql',
                               'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost',
                               'ORCHESTRATOR_beta_C68__shared.ArchiveInputsChanged',
                               'ORCHESTRATOR_beta_C68__shared.DeltaRequiresReconciliation',
                               'ORCHESTRATOR_beta_C68__shared.PollComplete',
                               'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure']},
          'exports': {'watching.poll_coverage.poll_coverage__shared.PollingProof': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'watching.poll_coverage.poll_coverage__shared.ArchiveCoverage': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'archive_operations.archive_operations__shared.ArchiveInputsChanged': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'archive_operations.archive_operations__shared.ArchiveCoverageLost': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'generation.generation__shared.WorkerIngestionFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'generation.generation__shared.DeltaRequiresReconciliation': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'watching.poll_coverage.watcher_poll_coverage.PollingProof': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'watching.poll_coverage.watcher_poll_coverage.ArchiveCoverage': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'watching.poll_coverage.watcher_diagnostics.report_fence_failure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'watching.poll_coverage.watcher_diagnostics.FenceDiagnostics': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'watching.watcher_poll': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching/poll_coverage']},
                      'watching.poll_coverage.watcher_diagnostics.report_graph_restart': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'archive_operations.archive_jobs._ARCHIVE_FENCE_MESSAGE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'watching.poll_coverage.watcher_diagnostics.report_graph_consistency': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.checkpoint.startup_checkpoint.archive_checkpoint': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'archive_operations.archive_jobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'watching.poll_coverage.watcher_diagnostics.emit_record': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'watching.poll_coverage.watcher_diagnostics.FOREGROUND_FENCE_MESSAGE': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'archive_operations.archive_jobs.ArchiveJobs': {'private': ['C68']},
                      'archive_operations.archive_jobs.ArchiveInputsChanged': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'archive_operations.archive_jobs.ArchiveCoverageLost': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'archive_operations.archive_jobs.ARCHIVE_RECONCILIATION': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},

                      'ORCHESTRATOR_beta_C68__shared.admit_generation': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'ORCHESTRATOR_beta_C68__shared.confirm_reuse': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'ORCHESTRATOR_beta_C68__shared.read_reuse': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.Connection': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/peers']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.ENGINE': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/peers']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.Kernel': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.RunFixture': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations/checkpoint']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.kernel_server': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations/checkpoint']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.latest': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.lifecycle_job': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation/restart', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.project': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/peers', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.project_jobs': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.request_json': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.restore_reuse': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation/restart', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.wait_for': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/peers', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher']},
                      'ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared.watch_project': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__tests.generation._worker_diagnostics_cases.WorkerDiagnosticsCases': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__tests.lifecycle.test_lifecycle_queries.database': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'abort.WorkerAborted': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.generation.CompilerColumnsChanged': {"private": ['C68']},
                      'generation.generation.DeltaRequiresReconciliation': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.generation.GenerationBaseChanged': {"private": ['C68']},
                      'generation.generation.MAX_WARM_DELTA_PATHS': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.generation.TICKET_ROOTS': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/watching']},
                      'generation.generation.WorkerIngestionFailure': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.generation.admit_generation': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.generation.confirm_reuse': {"private": ['C68']},
                      'generation.generation.live_reuse': {"private": ['C68']},
                      'generation.generation.parse_worker_result': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.generation.read_accepted_model': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.generation.read_reuse': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.generation.read_structure': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'generation.generation.replace_ingestion_issues': {"private": ['C68']},
                      'generation.generation.ticket_delta_paths': {"private": ['C68']},
                      'generation.generation.wait_build': {"private": ['C68']},
                      'generation.generation.worker_failure': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.generation.worker_request': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.generation_flow.GenerationFlow': {"private": ['C68']},
                      'generation.generation_live_capture.GenerationLiveCapture': {"private": ['C68']},
                      'generation.generation_requests.GenerationRequests': {"private": ['C68']},
                      'generation.startup_graph.StartupGraphJobs': {"private": ['C68']},
                      'generation.worker.checkpoint.startup_checkpoint.CHECKPOINT_FIELDS': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.checkpoint.startup_checkpoint.MAX_DELTA_PATHS': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.checkpoint.startup_checkpoint.ReuseRecord': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.checkpoint.startup_checkpoint.checkpoint_paths': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'generation.worker.checkpoint.startup_checkpoint.compatible_checkpoint': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'generation.worker.flow.Flow': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.flow.safe_target': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.generation_worker.ForegroundCoverageLost': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.generation_worker.ForegroundInputsChanged': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.generation_worker.GENERATION_ERRORS': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.generation_worker.GenerationWorker': {"private": ['C68']},
                      'generation.worker.warm_worker.WarmLifecycleUnavailable': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'generation.worker.warm_worker.run_lifecycle': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'generation.worker.worker_reply.parse_graph_result': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'generation.worker.worker_reply.parse_worker_result': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'jobs.ENGINE': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/peers']},
                      'jobs.FIELDS': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'jobs.LifecycleCoveragePending': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'jobs.UnixConnection': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'jobs._GenerationJob': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'jobs._LifecycleJob': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle']},
                      'jobs._Run': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/archive_operations']},
                      'jobs.operation_timeout': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/peers']},
                      'lifecycle.documents.atom_document.document': {"private": ['C68']},
                      'lifecycle.lifecycle.LifecycleJobs': {"private": ['C68']},
                      'lifecycle.lifecycle_queries.lifecycle_context': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket']},
                      'lifecycle.lifecycle_queries.lifecycle_sql': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle']},
                      'peers.project_admission.AdmissionClient': {"private": ['C68']},
                      'peers.project_admission._selection': {"private": ['C68']},
                      'peers.project_peers.ProjectBinding': {"private": ['C68']},
                      'peers.project_peers.open_project_peers': {"private": ['C68']},
                      'peers.project_peers.socket_path': {"private": ['C68']},
                      'peers.shared_host_config.load': {"private": ['C68']},
                      'peers.shared_project_pool.SharedProjectPool': {"private": ['C68']},
                      'peers.warm_worker_process.open_warm_worker': {"private": ['C68']},
                      'peers.warm_worker_process.process_environment': {"private": ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation/worker']},
                      'watching.retry.COVERAGE_RECOVERED': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'watching.retry.CurrentnessRetry': {"private": ['C68']},
                      'watching.retry.source_changed': {"private": ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/generation']},
                      'watching.watcher.SourceWatcher': {"private": ['C68']},
                      'watching.watcher_poll.PollComplete': {'private': ['C68', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket', 'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher']},'archive_jobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__shared.ArchiveInputsChanged': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__shared.DeltaRequiresReconciliation': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'ORCHESTRATOR_beta_C68__shared.PollComplete': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher']},
                      'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations']},
                      'lifecycle_queries.lifecycle_context': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle/socket']},
                      'lifecycle_queries.lifecycle_sql': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/lifecycle']},
                      'ORCHESTRATOR_beta_C68__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/archive_operations/checkpoint',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation/batches',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation/restart']},
                      'ORCHESTRATOR_beta_C68__shared.Flow': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.GenerationJobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/watcher',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation',
                          'LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests/generation/batches']}}},
 'io': {'server': {'project_peer_owner': {'transport': 'cli',
                                          'runner': 'managed_python',
                                          'module': 'ORCHESTRATOR_beta_C68.project_peer_owner',
                                          'arguments': 'selected Project '
                                                       'binding and peer '
                                                       'settings',
                                          'readiness': 'peers.ready after '
                                                       'bound peers '
                                                       'start'},
                   'shared_peer_owner': {'transport': 'newline-delimited '
                                                      'JSON over private '
                                                      'Unix socket',
                                         'runner': 'managed_python',
                                         'module': 'ORCHESTRATOR_beta_C68.shared_peer_owner',
                                         'arguments': ['--socket',
                                                       '<owner-socket>',
                                                       '--host-settings',
                                                       '<settings>'],
                                         'operations': ['select',
                                                        'status',
                                                        'lease']},
                   'jobs': {'transport': 'http',
                            'socket': 'private Unix socket',
                            'runner': 'managed_python',
                            'module': 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared',
                            'arguments': ['--socket',
                                          '<socket>',
                                          '--instance-id',
                                          '<instance-id>',
                                          '--binding-file',
                                          '<pinned-project-binding>',
                                          '--database-socket',
                                          '<kernel-socket>',
                                          'optional --watch-code',
                                          'optional paired '
                                          '--worker-socket and '
                                          '--worker-load-seconds'],
                            'routes': ['GET /health',
                                       'POST /jobs/build',
                                       'POST /jobs/abort',
                                       'POST /jobs/lifecycle',
                                       'GET /jobs/worker-runs'],
                            'build_request': ['instance_id',
                                              'root',
                                              'control_root',
                                              'manifest_path',
                                              'manifest_sha256',
                                              'project_prefix'],
                            'optional_build_field': 'refresh_target',
                            'abort_fields': ['instance_id', 'run_id'],
                            'active_fields': ['run_id', 'worker_alive'],
                            'abort_scope': ['cold generation',
                                            'accepted warm capture'],
                            'worker_mode': ['warm', 'cold'],
                            'build_timings': ['worker_seconds',
                                              'admission_seconds'],
                            'optional_delta_field': 'delta_path_count',
                            'lifecycle_request': 'build binding plus name '
                                                 'and arguments',
                            'lifecycle_result': ['lifecycle',
                                                 'write_state',
                                                 'projection']}},
        'client': {'snapshot_worker': {'component': 'C69',
                                       'transport': 'cli',
                                       'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                   'warm_ticket_delta': {'component': 'C69',
                                         'interface': 'warm_ticket_delta'},
                   'warm_indexed_lifecycle': {'component': 'C69',
                                              'interface': 'warm_indexed_lifecycle'},
                   'lifecycle_worker': {'component': 'C69',
                                        'interface': 'task_lifecycle',
                                        'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                   'database': {'component': 'C71',
                                'transport': 'http',
                                'routes': ['GET /generation/reuse',
                                           'GET /structure',
                                           'PUT /generation',
                                           'PUT /generation/native',
                                           'PUT /generation/native-delta',
                                           'POST /flow/events',
                                           'POST /database']}}},
 'state': {'reads': ['pinned Project binding',
                     'Project source change events',
                     'code and dependency file events when the Graph is '
                     'enabled'],
           'writes': ['active build, lifecycle request, latest Worker '
                      'outcome and admitted input proof in memory',
                      'candidate peer, warm Worker, and shared lease '
                      'state']}}
```

## Component Contract

### Run a pinned Beta snapshot Worker

#### Guarantee

For standalone operation, own the selected Project's peer pair and warm Worker.
Report readiness after its bound peers start. Stop them with their owner.
Apply AN-S-5192 to shared-mode Project selection, status, and leases.

Establish watcher coverage before capture. Admit the pinned Current and
Draft base and replay events through the completed observation before
Ready or affected writes. Leave later events queued. Require source proof
for uncovered inputs. On coverage loss, reconcile affected inputs and
broaden capture if the scope is unknown. Log failed source checks once to
stderr with run ID, phase, wait, and Project-relative evidence. Distinguish
source changes from coverage loss.

Serialize live builds and Kernel admissions at startup and on watched
changes. Watch Graph inputs when enabled. Follow AN-S-3389 for Archive
readiness. Load Archive in a separate Worker while live changes proceed.
Keep Archive pending until Kernel admits it. Report progress, failure,
and the separate readiness and Archive timing.

Use one Manifest Builder per Project. Coalesce input changes during a
build into one follow-up for the newest observed inputs. Submit its exact
Model and Structure together. Mark affected data pending and block
affected writes until that generation is admitted.

Serialize pinned rebuild requests with source changes. Requests for the
same target share one admission and result map. Reply after the fresh
generation is admitted, with result replacements or a typed failure.
Report the active build and latest outcome.

Serialize lifecycle jobs with generation builds. Use one admitted Kernel
generation for SQL allocation, history, containment, and replacements.
Supply the Model rules and Structure. Use an isolated warm Worker child
when configured, and coordinated capture for Ticket tree or Model changes.
Return the write outcome and native delta admission result. Preserve known
effects on projection failure. A lost response leaves the effect unknown.
Block further writes until complete recapture confirms the source.
Never repeat a write automatically.

Reuse the input proof only after Kernel acceptance. For watcher refresh,
pin the proof and the matching Structure when needed for non-Ticket work.
Submit native refresh, or native and Graph refresh, against the named base.
Full-build if the base changed. Explicit rebuilds use the full build path. Retry native
currentness failures with backoff. Report a failed Code Analyzer restart
as a build issue. Ignore delayed watcher events only when source matches
the retained effect, including absence.

Default to Incremental Startup after Worker verification and Kernel
confirmation of a compatible checkpoint. Reuse unchanged projection and
apply verified offline Current and Draft deltas. Apply AN-S-3334 to
checkpoint verification and Graph-only changes. Full reload also applies
when the database or checkpoint is missing.

Use native Ticket notifications when available and polling for missed
or other events. Send both rename paths. Collect events for 20 ms after
the first. For up to 32 distinct Ticket paths, wait for the warm Worker
at most the measured cold-load time, then use a fresh Worker if needed.
Send 33 through 1,024 paths to one fresh Worker. Broaden capture or
reconcile when the paths or base cannot be verified. Keep one admission
in flight per Project. Report mode, capture including startup, admission
time, and path count for the latest successful delta.

Report the active run ID and liveness of its cold Worker or warm child.
Wait for completion or explicit abort. Stop the aborted process group
and report that outcome. Exclude writes and Kernel admission from abort.
Bind fresh Workers to the current Orchestrator. They stop their process
group on owner loss. A replacement admits from Project state.

Send one causal trace of the trigger, accepted changes, effects, output,
and any clock-driven retry to the bound Kernel. Log publication errors.

#### References

AN-S-3337 and AN-T-2958.
