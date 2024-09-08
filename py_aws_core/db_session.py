import typing

from py_aws_core import const, decorators, db_dynamo, entities, exceptions, logs
from py_aws_core.db_dynamo import DDBClient, GetItemResponse

logger = logs.logger


class SessionDBAPI(db_dynamo.ABCCommonAPI):
    @classmethod
    def build_session_map(
        cls,
        session_id: str,
        b64_cookies: bytes,
        expire_in_seconds: int = const.DB_DEFAULT_EXPIRES_IN_SECONDS
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        return cls.get_batch_entity_create_map(
            expire_in_seconds=expire_in_seconds,
            pk=pk,
            sk=sk,
            _type=entities.Session.type(),
            Base64Cookies=b64_cookies,
        )

    class GetSessionItem:
        class Response(GetItemResponse):
            @property
            def session(self) -> entities.Session:
                return entities.Session(data=self.item)

        @classmethod
        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
        def call(cls, db_client: DDBClient, session_id: str) -> Response:
            pk = sk = entities.Session.create_key(_id=session_id)
            response = db_client.get_item(
                Key={
                    'PK': {'S': pk},
                    'SK': {'S': sk}
                },
                ExpressionAttributeNames={
                    "#pk": "PK",
                    "#ck": "Base64Cookies",
                    "#tp": "Type"
                },
                ProjectionExpression='#ck, #tp'
            )
            logger.debug(f'{cls.__qualname__}.call# -> response: {response}')
            return cls.Response(response)

    class PutSession:
        @classmethod
        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
        def call(cls, db_client: DDBClient, session_id: str, b64_cookies: bytes):
            pk = sk = entities.Session.create_key(_id=session_id)
            _type = entities.Session.type()
            item = SessionDBAPI.get_put_item_map(
                pk=pk,
                sk=sk,
                _type=_type,
                expire_in_seconds=None,
                Base64Cookies=b64_cookies,
            )
            response = db_client.put_item(
                Item=item,
            )
            logger.debug(f'{cls.__qualname__}.call# -> response: {response}')
            return response

    class UpdateSessionCookies:
        @classmethod
        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
        def call(
            cls,
            db_client: DDBClient,
            _id: str,
            b64_cookies: bytes
        ):
            pk = sk = entities.Session.create_key(_id=_id)
            return db_client.update_item(
                Key={
                    'PK': {'S': pk},
                    'SK': {'S': sk},
                },
                UpdateExpression='SET #b64 = :b64, #mda = :mda',
                ExpressionAttributeNames={
                    '#b64': 'Base64Cookies',
                    '#mda': 'ModifiedAt',
                },
                ExpressionAttributeValues={
                    ':b64': {'B': b64_cookies},
                    ':mda': {'S': SessionDBAPI.iso_8601_now_timestamp()}
                }
            )
