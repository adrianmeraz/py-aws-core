from . import logs, db_session, entities
from .db_dynamo import get_db_client
from .interfaces import IDatabase

db_client = get_db_client()
logger = logs.get_logger()


class DynamoDatabase(IDatabase):
    @classmethod
    def get_session(cls, session_id: str) -> entities.Session:
        return db_session.GetSessionItem.call(db_client=db_client, session_id=session_id).session

    @classmethod
    def get_or_create_session(cls, session_id: str) -> entities.Session:
        return db_session.GetOrCreateSession.call(
            db_client=db_client,
            session_id=session_id
        ).session

    @classmethod
    def put_session(cls, session_id: str, b64_cookies: bytes):
        logger.info(f'Writing cookies to database...', session_id=session_id)
        db_session.PutSession.call(
            db_client=db_client,
            session_id=session_id,
            b64_cookies=b64_cookies
        )
        logger.info(f'Wrote cookies to database', session_id=session_id)

    @classmethod
    def update_session_cookies(cls, session_id: str, b64_cookies: bytes) -> entities.Session:
        return db_session.UpdateSessionCookies.call(
            db_client=db_client,
            session_id=session_id,
            b64_cookies=b64_cookies
        ).session
