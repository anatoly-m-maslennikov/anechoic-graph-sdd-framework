"""Execute Local Release package and gate phases."""

from . import local_release_runner as r


class RunnerPhases:
    def _phase(self, phase):
        if phase == "validate inputs":
            self._validate_inputs(phase)
        elif phase == "bump candidate version":
            self._bump_version()
        elif phase in r._TEST_GATES:
            self._run_tests(phase)
        elif phase == "copy active sources":
            self._copy_sources()
        elif phase == "copy product to installed framework":
            self._copy_product()
        elif phase == "build package":
            self._build_package()
        elif phase == "prepare candidate image":
            self._prepare_image()
        elif phase == "install project runtime":
            self._install_runtime()
        else:
            self._start_mcp()

    def _validate_inputs(self, phase):
        self.failed_step = "validate_inputs"
        self.production_port = r.package_phases.validate_inputs(
            self.root,
            self.selection,
            self.product,
            self.installed,
            self.runtime,
        )
        if self._source_binding() is None:
            self.failed_step = "bump_candidate_version"
            r._read_version(self.root)

    def _run_tests(self, phase):
        self.failed_step = phase.replace(" ", "_")
        suite_phase = r._TEST_GATES[phase]
        log_phase = "image" if suite_phase == "image-tests" else suite_phase
        options = self._test_gate_options()
        options["functional_fast"] = self.functional_suite == "fast"
        if suite_phase == "canary" and self.canary_endpoint is not None:
            r._verify_package(self.package, self.package_identity)
            if "image" in self.test_log_paths:
                self.test_log_paths.setdefault(
                    "canary", self.test_log_paths["image"]
                )
            self.test_log_path = self.test_log_paths.get("canary")
            return
        try:
            observed_endpoint = r.run_gate(
                self.root,
                suite_phase,
                self.candidate_image,
                self.package,
                self.package_identity,
                self.selection,
                self.run_id,
                None if self.default_runner else self.runner,
                self.test_log_paths,
                verify=r._verify_package,
                target=r._target,
                named_file=r.tempfile.NamedTemporaryFile,
                logged_process=r.partial(
                    r.run_logged_test_process,
                    lock_fd=self.lock_fd,
                    check_abort=self.journal.check_abort,
                ),
                failed_output=r._failed_test_output,
                record_logs=self.journal.record_logs,
                **options,
            )
        finally:
            self.test_log_path = self.test_log_paths.get(log_phase)
        if observed_endpoint is not None and self.canary_endpoint is None:
            self.canary_endpoint = observed_endpoint
        return observed_endpoint

    def _test_gate_options(self):
        return {}

    def _copy_sources(self):
        self.failed_step = "copy_active_sources"
        r.package_phases.copy_sources(
            self.root, self.selection, self.run_id, self.product
        )

    def _copy_product(self):
        self.failed_step = "copy_product_to_installed_framework"
        r.package_phases.copy_product(
            self.root,
            self.selection,
            self.installation_lock,
            self.package,
            self.package_identity,
            self.prepared_product,
            self.product_identity,
            self.installed,
        )

    def _build_package(self):
        self.failed_step = "build_package"
        self.staging = r._new_staging_directory(self.root, f"{self.run_id}-")
        self.journal.data["staging"] = self.staging.relative_to(
            self.root
        ).as_posix()
        self.journal.save()
        (
            self.prepared_product,
            self.product_identity,
            self.package,
            self.package_identity,
        ) = r.package_phases.build_package(
            self.root, self.selection, self.product, self.staging
        )

    def _prepare_image(self):
        self.failed_step = "prepare_candidate_image"
        self.manager, self.candidate_image, self.candidate_fingerprint = (
            r.package_phases.prepare_image(
                self.root,
                self.selection,
                self.staging,
                self.package,
                self.package_identity,
                self.prepared_product,
                self.product_identity,
                self.cleanup_runner,
                provenance=self._image_provenance(),
            )
        )

    def _install_runtime(self):
        self.failed_step = "install_project_runtime"
        r.package_phases.install_runtime(
            self.root,
            self.package,
            self.package_identity,
            self.runtime,
            self.candidate_image,
            self.candidate_fingerprint,
        )
