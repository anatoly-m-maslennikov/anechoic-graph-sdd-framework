"""Read launcher identity for tests of the Release image contract."""

from functools import partial

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import ImageManager


def packaged_identity_reader(root):
    launcher = ImageManager(root, project_root=root)
    return partial(launcher.identity, use_packaged_assets=True)
