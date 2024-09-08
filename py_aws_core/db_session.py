from py_aws_core import decorators, db_dynamo, entities, exceptions, logs
from py_aws_core.db_dynamo import DDBClient, GetItemResponse, UpdateItemResponse

logger = logs.logger


class SessionDDBAPI(db_dynamo.ABCCommonAPI):
    pass


class GetSessionItem(SessionDDBAPI):
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


class PutSession(SessionDDBAPI):
    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(cls, db_client: DDBClient, session_id: str, b64_cookies: bytes):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        item = cls.get_put_item_map(
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


class UpdateSessionCookies(SessionDDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        db_client: DDBClient,
        session_id: str,
        b64_cookies: bytes
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        response = db_client.update_item(
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
                ':mda': {'S': cls.iso_8601_now_timestamp()}
            },
            ReturnValues='ALL_NEW'
        )
        logger.debug(f'{cls.__qualname__}.call# -> response: {response}')
        return cls.Response(response)
