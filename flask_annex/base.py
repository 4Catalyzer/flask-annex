from . import utils

# -----------------------------------------------------------------------------


class AnnexBase:
    @classmethod
    def from_env(cls, namespace):
        return cls(**utils.get_config_from_env(namespace))

    def delete(self, key):
        raise NotImplementedError()

    def delete_many(self, keys):
        raise NotImplementedError()

    def get_file(self, key, out_file):
        raise NotImplementedError()

    def list_keys(self, prefix):
        raise NotImplementedError()

    def save_file(self, key, in_file):
        raise NotImplementedError()

    def send_file(self, key):
        raise NotImplementedError()

    def get_upload_info(self, key):
        raise NotImplementedError()
