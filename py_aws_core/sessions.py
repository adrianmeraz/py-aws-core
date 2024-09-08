from abc import ABC, abstractmethod


class ABCPersistSession(ABC):
    @abstractmethod
    def read_session(self):
        pass

    @abstractmethod
    def write_session(self, value):
        pass
