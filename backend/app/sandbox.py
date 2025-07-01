def run_in_sandbox(code: str) -> str:
    client = docker.from_env()
    container = client.containers.run(
        "python:3.9-slim",
        command=f"python -c '{code}'",
        volumes={'google-creds.json': {'bind': '/creds.json', 'mode': 'ro'}},
        remove=True
    )
    return container.decode()
