from py_aws_core import const, decorators, db_dynamo, entities, exceptions, logs
from py_aws_core.db_dynamo import DDBClient, DDBItemResponse, UpdateItemResponse

logger = logs.get_logger()


class SessionDDBAPI(db_dynamo.ABCCommonAPI):
    pass


class GetOrCreateSession(SessionDDBAPI):
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.attributes)

    @classmethod
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(cls, db_client: DDBClient, session_id: str):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        now = cls.iso_8601_now_timestamp()
        update_fields = [
            cls.UpdateField(expression_attr='ty'),
            cls.UpdateField(expression_attr='si'),
            cls.UpdateField(expression_attr='ma'),
            cls.UpdateField(expression_attr='ea', set_once=True),
            cls.UpdateField(expression_attr='ca', set_once=True),
        ]
        response = db_client.update_item(
            Key={
                'PK': {'S': pk},
                'SK': {'S': sk},
            },
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
                ':ca': now,
                ':ma': now,
                ':ea': cls.calc_expire_at_timestamp(expire_in_seconds=const.DB_DEFAULT_EXPIRES_IN_SECONDS),
            }),
            ReturnValues='ALL_NEW'
        )

        logger.debug(f'response: {response}')
        return cls.Response(response)


class GetSessionItem(SessionDDBAPI):
    class Response(DDBItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.Item)

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
                "#bc": "Base64Cookies",
                "#tp": "Type"
            },
            ProjectionExpression='#pk, #bc, #tp'
        )
        logger.debug(f'response: {response}')
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
            SessionId=session_id
        )
        response = db_client.put_item(
            Item=item,
        )
        logger.debug(f'response: {response}')
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
        logger.debug(f'response: {response}')
        return cls.Response(response)
