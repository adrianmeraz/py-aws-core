from py_aws_core.dynamodb_service import DynamoDBService
from . import logs, db_session, entities
from .db_interface import IDatabase

logger = logs.get_logger()


class DatabaseService(IDatabase):
    def __init__(self, dynamodb_client: DynamoDBService):
        self._dynamodb_client = dynamodb_client

    def get_session(self, session_id: str) -> entities.Session:
        r_get_session_item = db_session.GetSessionItem.call(db_client=self._dynamodb_client, session_id=session_id)
        return r_get_session_item.session

    def get_or_create_session(self, session_id: str) -> entities.Session:
        return db_session.GetOrCreateSession.call(
            db_client=self._dynamodb_client,
            session_id=session_id
        ).session

    def put_session(self, session_id: str, b64_cookies: bytes):
        logger.info(f'Writing cookies to database...', session_id=session_id)
        db_session.PutSession.call(
            db_client=self._dynamodb_client,
            session_id=session_id,
            b64_cookies=b64_cookies
        )
        logger.info(f'Wrote cookies to database', session_id=session_id)

    def update_session_cookies(self, session_id: str, b64_cookies: bytes) -> entities.Session:
        return db_session.UpdateSessionCookies.call(
            db_client=self._dynamodb_client,
            session_id=session_id,
            b64_cookies=b64_cookies
        ).session
