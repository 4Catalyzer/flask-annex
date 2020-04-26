from . import utils

# -----------------------------------------------------------------------------


def get_annex_class(storage):
    if storage == "file":
        from .file import FileAnnex

        return FileAnnex
    elif storage == "s3":
        from .s3 import S3Annex

        return S3Annex
    else:
        raise ValueError(f"unsupported storage {storage}")


# -----------------------------------------------------------------------------


# We don't use the base class here, as this is just a convenience thing rather
# than an actual annex class.
class Annex:
    def __new__(cls, storage, *args, **kwargs):
        annex_class = get_annex_class(storage)
        return annex_class(*args, **kwargs)

    @staticmethod
    def from_env(namespace):
        storage = utils.get_config_from_env(namespace)["storage"]

        # Use storage-specific env namespace when configuring a generic annex,
        # to avoid having unrecognized extra keys when changing storage.
        storage_namespace = f"{namespace}_{storage.upper()}"

        annex_class = get_annex_class(storage)
        return annex_class.from_env(storage_namespace)
