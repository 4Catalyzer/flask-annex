from abc import ABCMeta, abstractmethod
from six import with_metaclass

from . import utils

# -----------------------------------------------------------------------------


class AnnexBase(with_metaclass(ABCMeta, object)):
    @classmethod
    def from_env(cls, namespace):
        return cls(**utils.get_config_from_env(namespace))

    @abstractmethod
    def save_file(self, key, filename):
        raise NotImplementedError()

    @abstractmethod
    def send_file(self, key, **options):
        raise NotImplementedError()
