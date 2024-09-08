import entities
from . import logs
from .db_session import SessionDBAPI
from .db_dynamo import get_db_client
from .interfaces import IDatabase


db_client = get_db_client()
logger = logs.logger


class DynamoDatabase(IDatabase):
    @classmethod
    def get_session(cls, session_id: str) -> entities.Session:
        return SessionDBAPI.GetSessionItem.call(db_client=db_client, session_id=session_id).session

    @classmethod
    def put_session(cls, session_id: str, b64_cookies: bytes):
        return SessionDBAPI.PutSession.call(
            db_client=db_client,
            session_id=session_id,
            b64_cookies=b64_cookies
        )
