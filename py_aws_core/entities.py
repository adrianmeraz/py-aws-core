import typing
from abc import ABC, abstractmethod

from py_aws_core import db_dynamo, encoders


class BaseModel:
    def __init__(self, data):
        self.__data = self.deserialize_data(data)
        self.PK = self.data.get('PK')
        self.SK = self.data.get('SK')
        self.Type = self.data.get('Type')
        self.CreatedAt = self.data.get('CreatedAt')
        self.CreatedBy = self.data.get('CreatedBy')
        self.ModifiedAt = self.data.get('ModifiedAt')
        self.ModifiedBy = self.data.get('ModifiedBy')
        self.ExpiresAt = self.data.get('ExpiresAt')

    @property
    def data(self):
        return self.__data

    @property
    def to_json(self):
        return encoders.JsonEncoder().serialize_to_json(self)

    @staticmethod
    def deserialize_data(data: dict) -> typing.Dict:
        return db_dynamo.ABCCommonAPI.deserialize_types(data)


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
        self.Base64Cookies = self.data.get('Base64Cookies')
        self.SessionId = self.data.get('SessionId')

    @classmethod
    def create_key(cls, _id: str) -> str:
        return f'{cls.type()}#{str(_id)}'

    @property
    def b64_cookies_bytes(self):
        if self.Base64Cookies:
            return self.Base64Cookies.value
        return None
