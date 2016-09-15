from abc import ABCMeta, abstractmethod

from .compat import with_metaclass
from . import utils

# -----------------------------------------------------------------------------


class AnnexBase(with_metaclass(ABCMeta, object)):
    @classmethod
    def from_env(cls, namespace):
        return cls(**utils.get_config_from_env(namespace))

    @abstractmethod
    def delete(self, key):
        raise NotImplementedError()

    @abstractmethod
    def delete_many(self, keys):
        raise NotImplementedError()

    @abstractmethod
    def get_file(self, key, out_file):
        raise NotImplementedError()

    @abstractmethod
    def list_keys(self, prefix):
        raise NotImplementedError()

    @abstractmethod
    def save_file(self, key, in_file):
        raise NotImplementedError()

    @abstractmethod
    def send_file(self, key):
        raise NotImplementedError()
