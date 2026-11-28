"""Watcher callback path and operation cases."""


class WatcherCallbackCases:
    def test_file_callbacks_keep_selected_repository_relative_paths(
        self,
    ) -> None:
        path = self.control / "04_requirement/CA-R-1.md"
        self.observer.handler.on_created(self.event(path))
        self.observer.handler.on_modified(self.event(path))
        self.observer.handler.on_deleted(self.event(path))

        self.assertEqual(
            [
                {
                    "operation": "create",
                    "old_path": None,
                    "new_path": ".anechoic_example/04_requirement/CA-R-1.md",
                },
                {
                    "operation": "update",
                    "old_path": None,
                    "new_path": ".anechoic_example/04_requirement/CA-R-1.md",
                },
                {
                    "operation": "remove",
                    "old_path": ".anechoic_example/04_requirement/CA-R-1.md",
                    "new_path": None,
                },
            ],
            self.watcher.changes(0),
        )

    def test_moves_keep_native_boundary_and_parent_meaning(self) -> None:
        old = self.control / "04_requirement/CA-R-1.md"
        renamed = self.control / "04_requirement/CA-R-2.md"
        moved = self.control / "05_method/CA-R-2.md"
        outside = self.root / "outside.md"
        self.observer.handler.on_moved(self.event(old, destination=renamed))
        self.observer.handler.on_moved(self.event(renamed, destination=moved))
        self.observer.handler.on_moved(self.event(outside, destination=old))
        self.observer.handler.on_moved(self.event(moved, destination=outside))
        self.observer.handler.on_moved(
            self.event(outside, destination=self.root / "elsewhere.md")
        )

        self.assertEqual(
            [
                {
                    "operation": "rename",
                    "old_path": ".anechoic_example/04_requirement/CA-R-1.md",
                    "new_path": ".anechoic_example/04_requirement/CA-R-2.md",
                },
                {
                    "operation": "move",
                    "old_path": ".anechoic_example/04_requirement/CA-R-2.md",
                    "new_path": ".anechoic_example/05_method/CA-R-2.md",
                },
                {
                    "operation": "create",
                    "old_path": None,
                    "new_path": ".anechoic_example/04_requirement/CA-R-1.md",
                },
                {
                    "operation": "remove",
                    "old_path": ".anechoic_example/05_method/CA-R-2.md",
                    "new_path": None,
                },
            ],
            self.watcher.changes(0),
        )

    def test_directory_create_move_remove_are_kept_but_modify_is_ignored(
        self,
    ) -> None:
        directory = self.control / "04_requirement"
        other = self.control / "nested/05_method"
        self.observer.handler.on_created(self.event(directory, directory=True))
        self.observer.handler.on_modified(
            self.event(directory, directory=True)
        )
        self.observer.handler.on_moved(
            self.event(directory, destination=other, directory=True)
        )
        self.observer.handler.on_deleted(self.event(other, directory=True))

        self.assertEqual(
            [
                {
                    "operation": "create",
                    "old_path": None,
                    "new_path": ".anechoic_example/04_requirement",
                },
                {
                    "operation": "move",
                    "old_path": ".anechoic_example/04_requirement",
                    "new_path": ".anechoic_example/nested/05_method",
                },
                {
                    "operation": "remove",
                    "old_path": ".anechoic_example/nested/05_method",
                    "new_path": None,
                },
            ],
            self.watcher.changes(0),
        )
