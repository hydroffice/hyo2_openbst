from abc import ABC, abstractmethod

import logging

logger = logging.getLogger(__name__)


class AbstractRawFile(ABC):
    """Common raw file class"""

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.file = None
        self.file_is_open = False
        self.mapped = False

    # File/Data Interaction
    @abstractmethod
    def data_map(self):
        pass

    @abstractmethod
    def is_mapped(self):
        pass

    @abstractmethod
    def get_datagram(self, dg_type):
        pass

    @staticmethod
    @abstractmethod
    def get_time():
        pass

    # Generic attribute retrieval
    @abstractmethod
    def get_beam_averages(self):
        pass

    @abstractmethod
    def get_snippets(self):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def get_attitude(self):
        pass

    @abstractmethod
    def get_tvg(self):
        pass

    @abstractmethod
    def get_static_gain(self):
        pass
