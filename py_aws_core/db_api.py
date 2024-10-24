from py_aws_core import decorators, dynamodb_entities, exceptions, logs
from py_aws_core.boto_responses import ItemResponse, UpdateItemResponse
from py_aws_core.dynamodb_api import DynamoDBAPI

logger = logs.get_logger()


class GetOrCreateSession(DynamoDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> dynamodb_entities.Session:
            return dynamodb_entities.Session(data=self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        table,
        session_id: str,
        created_at_datetime: str,
        expires_at: int = None
    ):
        pk = sk = dynamodb_entities.Session.create_key(_id=session_id)
        _type = dynamodb_entities.Session.type()
        update_fields = [
            cls.UpdateField(expression_attr='ty'),
            cls.UpdateField(expression_attr='si'),
            cls.UpdateField(expression_attr='ma'),
            cls.UpdateField(expression_attr='ea', set_once=True),
            cls.UpdateField(expression_attr='ca', set_once=True),
        ]
        response = table.update_item(
            Key={
                'PK': pk,
                'SK': sk,
            },
            UpdateExpression=cls.build_update_expression(update_fields),
            ExpressionAttributeNames={
                '#ty': 'Type',
                "#si": 'SessionId',
                '#ca': 'CreatedAt',
                '#ma': 'ModifiedAt',
                '#ea': 'ExpiresAt',
            },
            ExpressionAttributeValues={
                ':ty': _type,
                ':si': session_id,
                ':ca': created_at_datetime,
                ':ma': created_at_datetime,
                ':ea': expires_at,
            },
            ReturnValues='ALL_NEW'
        )

        logger.debug(f'GetOrCreateSession called', response=response)
        return cls.Response(response)


class GetSessionItem(DynamoDBAPI):
    class Response(ItemResponse):
        @property
        def session(self) -> dynamodb_entities.Session:
            return dynamodb_entities.Session(data=self.Item)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        table,
        session_id: str
    ) -> Response:
        pk = sk = dynamodb_entities.Session.create_key(_id=session_id)
        response = table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            },
            ExpressionAttributeNames={
                "#pk": "PK",
                "#bc": "Base64Cookies",
                "#tp": "Type"
            },
            ProjectionExpression='#pk, #bc, #tp'
        )
        logger.debug(f'GetSessionItem called', response=response)
        return cls.Response(response)


class PutSession(DynamoDBAPI):
    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        table,
        session_id: str,
        b64_cookies: bytes
    ):
        pk = sk = dynamodb_entities.Session.create_key(_id=session_id)
        _type = dynamodb_entities.Session.type()
        item = cls.get_put_item_map(
            pk=pk,
            sk=sk,
            _type=_type,
            expire_in_seconds=None,
            Base64Cookies=b64_cookies,
            SessionId=session_id
        )
        response = table.put_item(
            Item=item,
        )
        logger.debug(f'PutSession called', response=response)
        return response


class UpdateSessionCookies(DynamoDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> dynamodb_entities.Session:
            return dynamodb_entities.Session(self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        table,
        session_id: str,
        b64_cookies: bytes,
        now_datetime: str
    ):
        pk = sk = dynamodb_entities.Session.create_key(_id=session_id)
        response = table.update_item(
            Key={
                'PK': pk,
                'SK': sk,
            },
            UpdateExpression='SET #b64 = :b64, #mda = :mda',
            ExpressionAttributeNames={
                '#b64': 'Base64Cookies',
                '#mda': 'ModifiedAt',
            },
            ExpressionAttributeValues={
                ':b64': b64_cookies,
                ':mda': now_datetime
            },
            ReturnValues='ALL_NEW'
        )
        logger.debug(f'UpdateSessionCookies called', response=response)
        return cls.Response(response)
