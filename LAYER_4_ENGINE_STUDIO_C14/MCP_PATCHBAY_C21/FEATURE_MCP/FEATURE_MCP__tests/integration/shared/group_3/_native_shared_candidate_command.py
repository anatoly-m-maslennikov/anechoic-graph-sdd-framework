"""Build the shared candidate's disposable Docker invocation."""


def shared_candidate_command(host, settings, name, image, docker_deadline_env):
    return [
        "docker",
        "run",
        "--detach",
        "--pull=never",
        "--init",
        "--read-only",
        "--name",
        name,
        "--label",
        "anechoic.test=shared-candidate",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--tmpfs",
        "/tmp:size=128m,mode=1777",
        "--memory",
        "1536m",
        "--publish",
        "127.0.0.1::8092",
        "--mount",
        f"type=bind,src={host},dst={host}",
        "-e",
        f"ANECHOIC_HOST_SETTINGS={settings}",
        "-e",
        docker_deadline_env(),
        image,
        "shared-mcp",
    ]
