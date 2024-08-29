import typing

from py_aws_core import const, decorators, db_dynamo, entities, exceptions, logs
from py_aws_core.db_dynamo import DDBClient

logger = logs.logger


class SessionDBAPI(db_dynamo.ABCCommonAPI):
    @classmethod
    def build_session_map(
        cls,
        _id: str,
        b64_cookies: bytes,
        expire_in_seconds: int = const.DB_DEFAULT_EXPIRES_IN_SECONDS
    ):
        pk = sk = entities.Session.create_key(_id=_id)
        return cls.get_batch_entity_create_map(
            expire_in_seconds=expire_in_seconds,
            pk=pk,
            sk=sk,
            _type=entities.Session.type(),
            Base64Cookies=b64_cookies,
        )

    class GetSessionQuery:
        class Response(db_dynamo.QueryResponse):
            @property
            def sessions(self) -> typing.List[entities.Session]:
                return [entities.Session(s) for s in self.get_by_type(entities.Session.TYPE)]

            @property
            def session_b64_cookies(self):
                return self.sessions[0].Base64Cookies.value

        @classmethod
        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
        def call(
            cls,
            db_client: DDBClient,
            _id: str,
        ) -> Response:
            pk = entities.Session.create_key(_id=_id)
            response = db_client.query(
                KeyConditionExpression="#pk = :pk",
                ExpressionAttributeNames={
                    "#pk": "PK",
                    "#cookies": "Base64Cookies",
                    "#typ": "Type"
                },
                ExpressionAttributeValues={
                    ":pk": {"S": pk},
                },
                ProjectionExpression='#cookies, #typ'
            )
            logger.debug(f'{cls.__qualname__}.call#: response: {response}')
            return cls.Response(response)

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
