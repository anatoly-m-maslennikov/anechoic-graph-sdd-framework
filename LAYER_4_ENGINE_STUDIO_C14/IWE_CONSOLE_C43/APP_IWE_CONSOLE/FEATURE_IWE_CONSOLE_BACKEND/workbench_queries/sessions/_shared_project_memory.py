"""Track recently selected project identities."""


def remember_project(projects, selection):
    prefix, identity = selection.project_prefix, selection.instance_id
    project = {"prefix": prefix, "instance_id": identity}
    projects.pop(identity, None)
    projects[identity] = project
    if len(projects) > 32:
        projects.pop(next(iter(projects)))
    return project
