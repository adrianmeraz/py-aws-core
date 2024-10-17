from botocore.client import BaseClient

from py_aws_core import const, dynamodb_api, logs, utils

logger = logs.get_logger()


class SessionService:
    def __init__(self, boto_client: BaseClient, dynamodb_table_name: str):
        self._boto_client = boto_client
        self._dynamodb_table_name = dynamodb_table_name

    def get_or_create_session(self, session_id: str):
        return dynamodb_api.GetOrCreateSession.call(
            boto_client=self._boto_client,
            table_name=self._dynamodb_table_name,
            session_id=session_id,
            created_at_datetime=utils.to_iso_8601(),
            expires_at=dynamodb_api.calc_expire_at_timestamp(expire_in_seconds=const.DB_DEFAULT_EXPIRES_IN_SECONDS)
        )

    def get_session_item(self, session_id: str):
        return dynamodb_api.GetSessionItem.call(
            boto_client=self._boto_client,
            table_name=self._dynamodb_table_name,
            session_id=session_id
        )

    def put_session_item(self, session_id: str, b64_cookies: bytes):
        return dynamodb_api.PutSession.call(
            boto_client=self._boto_client,
            table_name=self._dynamodb_table_name,
            session_id=session_id,
            b64_cookies=b64_cookies
        )

    def update_session_cookies(self, session_id: str, b64_cookies: bytes):
        return dynamodb_api.UpdateSessionCookies.call(
            boto_client=self._boto_client,
            table_name=self._dynamodb_table_name,
            session_id=session_id,
            b64_cookies=b64_cookies,
            now_datetime=utils.to_iso_8601()
        )
