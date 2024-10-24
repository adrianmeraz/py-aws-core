import typing
from abc import ABC, abstractmethod

from py_aws_core import encoders
from py_aws_core.dynamodb_api import DynamoDBAPI


class BaseModel:
    def __init__(self, data):
        self.PK = data.get('PK')
        self.SK = data.get('SK')
        self.Type = data.get('Type')
        self.CreatedAt = data.get('CreatedAt')
        self.CreatedBy = data.get('CreatedBy')
        self.ModifiedAt = data.get('ModifiedAt')
        self.ModifiedBy = data.get('ModifiedBy')
        self.ExpiresAt = data.get('ExpiresAt')

    @property
    def to_json(self):
        return encoders.JsonEncoder().serialize_to_json(self)

    @staticmethod
    def deserialize_data(data: dict) -> typing.Dict:
        return DynamoDBAPI.deserialize_types(data)


class ABCEntity(ABC, BaseModel):
    TYPE = 'ABC'

    @classmethod
    @abstractmethod
    def create_key(cls, *args, **kwargs) -> str:
        pass

    @classmethod
    def type(cls) -> str:
        return cls.TYPE


class Session(ABCEntity):
    TYPE = 'SESSION'

    def __init__(self, data):
        super().__init__(data)
        self.Base64Cookies = data.get('Base64Cookies')
        self.SessionId = data.get('SessionId')

    @classmethod
    def create_key(cls, _id: str) -> str:
        return f'{cls.type()}#{str(_id)}'

    @property
    def b64_cookies_bytes(self):
        if self.Base64Cookies:
            return self.Base64Cookies.value
        return None
