from abc import ABC, abstractmethod

from . import entities


class IDatabase(ABC):

    @classmethod
    @abstractmethod
    def get_session(cls, session_id: str) -> entities.Session:
        pass

    @classmethod
    @abstractmethod
    def get_or_create_session(cls, session_id: str) -> entities.Session:
        pass

    @classmethod
    @abstractmethod
    def put_session(cls, session_id: str, b64_cookies: bytes):
        pass

    @classmethod
    @abstractmethod
    def update_session_cookies(cls, session_id: str, b64_cookies: bytes) -> entities.Session:
        pass
