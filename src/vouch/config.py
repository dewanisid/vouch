from collections.abc import Mapping

class MissingConfigError(Exception):
    """A required environment variable is not set."""

def require_env(name: str, env: Mapping[str, str]) -> str:
    value = env.get(name)
    if not value:
        raise MissingConfigError(f"missing required environment variable: {name}")

    return value
