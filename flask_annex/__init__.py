from .base import AnnexBase
from . import utils

# -----------------------------------------------------------------------------


def get_annex_class(storage):
    if storage == 'file':
        from .file import FileAnnex
        return FileAnnex
    elif storage == 's3':
        from .s3 import S3Annex
        return S3Annex
    else:
        raise ValueError("unsupported storage {}".format(storage))


# -----------------------------------------------------------------------------


# We can't use the base class here, as this does not explicitly implement the
# abstract methods.
class Annex(object):
    def __init__(self, storage, **kwargs):
        annex_class = get_annex_class(storage)

        # Proxy the actual implementation to prevent use of storage-specific
        # attributes when using the generic annex.
        self._impl = annex_class(**kwargs)

    @classmethod
    def from_env(cls, namespace):
        storage = utils.get_config_from_env(namespace)['storage']

        # Use storage-specific env namespace when configuring a generic annex,
        # to avoid having unrecognized extra keys when changing storage.
        storage_namespace = '{}_{}'.format(namespace, storage.upper())
        storage_config = utils.get_config_from_env(storage_namespace)

        return cls(storage, **storage_config)

    def __getattr__(self, item):
        # Only expose explicitly available abstract annex methods.
        if item in AnnexBase.__abstractmethods__:
            return getattr(self._impl, item)
        else:
            raise AttributeError
