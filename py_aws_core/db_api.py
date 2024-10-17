from botocore.client import BaseClient

from py_aws_core import decorators, entities, exceptions, logs
from py_aws_core.dynamodb_api import DynamoDBAPI
from py_aws_core.dynamodb_entities import ItemResponse, UpdateItemResponse

logger = logs.get_logger()


class GetOrCreateSession(DynamoDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        created_at_datetime: str,
        expires_at: int = None
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        update_fields = [
            cls.UpdateField(expression_attr='ty'),
            cls.UpdateField(expression_attr='si'),
            cls.UpdateField(expression_attr='ma'),
            cls.UpdateField(expression_attr='ea', set_once=True),
            cls.UpdateField(expression_attr='ca', set_once=True),
        ]
        response = boto_client.update_item(
            TableName=table_name,
            Key=cls.serialize_types({
                'PK': pk,
                'SK': sk,
            }),
            UpdateExpression=cls.build_update_expression(update_fields),
            ExpressionAttributeNames={
                '#ty': 'Type',
                "#si": 'SessionId',
                '#ca': 'CreatedAt',
                '#ma': 'ModifiedAt',
                '#ea': 'ExpiresAt',
            },
            ExpressionAttributeValues=cls.serialize_types({
                ':ty': _type,
                ':si': session_id,
                ':ca': created_at_datetime,
                ':ma': created_at_datetime,
                ':ea': expires_at,
            }),
            ReturnValues='ALL_NEW'
        )

        logger.debug(f'response: {response}')
        return cls.Response(response)


class GetSessionItem(DynamoDBAPI):
    class Response(ItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.Item)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        boto_client: BaseClient,
        table_name: str,
        session_id: str
    ) -> Response:
        pk = sk = entities.Session.create_key(_id=session_id)
        response = boto_client.get_item(
            TableName=table_name,
            Key=cls.serialize_types({
                'PK': pk,
                'SK': sk
            }),
            ExpressionAttributeNames={
                "#pk": "PK",
                "#bc": "Base64Cookies",
                "#tp": "Type"
            },
            ProjectionExpression='#pk, #bc, #tp'
        )
        logger.debug(f'response: {response}')
        return cls.Response(response)


class PutSession(DynamoDBAPI):
    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        b64_cookies: bytes
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        item = cls.get_put_item_map(
            pk=pk,
            sk=sk,
            _type=_type,
            expire_in_seconds=None,
            Base64Cookies=b64_cookies,
            SessionId=session_id
        )
        response = boto_client.put_item(
            TableName=table_name,
            Item=item,
        )
        logger.debug(f'response: {response}')
        return response


class UpdateSessionCookies(DynamoDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        cls,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        b64_cookies: bytes,
        now_datetime: str
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        response = boto_client.update_item(
            TableName=table_name,
            Key=cls.serialize_types({
                'PK': pk,
                'SK': sk,
            }),
            UpdateExpression='SET #b64 = :b64, #mda = :mda',
            ExpressionAttributeNames={
                '#b64': 'Base64Cookies',
                '#mda': 'ModifiedAt',
            },
            ExpressionAttributeValues=cls.serialize_types({
                ':b64': b64_cookies,
                ':mda': now_datetime
            }),
            ReturnValues='ALL_NEW'
        )
        logger.debug(f'response: {response}')
        return cls.Response(response)
