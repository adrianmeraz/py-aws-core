from abc import ABC, abstractmethod


class ISession(ABC):
    @abstractmethod
    def read_session(self):
        pass

    @abstractmethod
    def write_session(self, value):
        pass
