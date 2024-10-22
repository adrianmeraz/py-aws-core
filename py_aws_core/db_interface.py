from abc import ABC, abstractmethod

from . import dynamodb_entities


class IDatabase(ABC):
    @classmethod
    @abstractmethod
    def get_or_create_session(cls, session_id: str) -> dynamodb_entities.Session:
        pass

    @classmethod
    @abstractmethod
    def get_session_item(cls, session_id: str) -> dynamodb_entities.Session:
        pass

    @classmethod
    @abstractmethod
    def put_session_item(cls, session_id: str, b64_cookies: bytes):
        pass

    @classmethod
    @abstractmethod
    def update_session_cookies(cls, session_id: str, b64_cookies: bytes) -> dynamodb_entities.Session:
        pass
