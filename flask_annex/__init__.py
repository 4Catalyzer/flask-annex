from .base import AnnexBase

__all__ = ('Annex',)

# -----------------------------------------------------------------------------


def get_annex_class(storage):
    if storage == 'file':
        from .file import FileAnnex
        return FileAnnex
    else:
        raise ValueError("unsupported storage {}".format(storage))


# -----------------------------------------------------------------------------


class Annex(AnnexBase):
    def __init__(self, storage, **kwargs):
        annex_class = get_annex_class(storage)

        # Proxy the actual implementation to prevent use of storage-specific
        # attributes when using the generic annex.
        self._impl = annex_class(**kwargs)

    def save_file(self, key, filename):
        return self._impl.save_file(key, filename)

    def send_file(self, key, **options):
        return self._impl.send_file(key, **options)
