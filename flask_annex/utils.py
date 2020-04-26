import os

# -----------------------------------------------------------------------------


def get_config_from_env(namespace):
    prefix = f"{namespace}_"

    return {
        key[len(prefix) :].lower(): value
        for key, value in os.environ.items()
        if key.startswith(prefix)
    }
