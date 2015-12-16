import os

# -----------------------------------------------------------------------------


def get_config_from_env(namespace):
    prefix = '{}_'.format(namespace)

    return {
        key[len(prefix):].lower(): value
        for key, value in os.environ.items()
        if key.startswith(prefix)
    }
