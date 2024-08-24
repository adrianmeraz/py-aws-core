from abc import ABC, abstractmethod

from boto3.dynamodb import types

from py_aws_core import encoders


class BaseModel:
    def __init__(self, data):
        self.__data = self.to_normalized_data(data)
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

    @staticmethod
    def to_normalized_data(data: dict) -> dict:
        """
        Converts low level dynamo json to normalized json
        """
        return {k: types.TypeDeserializer().deserialize(v) for k, v in data.items()}

    @property
    def to_json(self):
        return encoders.DBEncoder().serialize_to_json(self)


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
        self.Base64Cookies = self.data['Base64Cookies']

    @classmethod
    def create_key(cls, _id: str) -> str:
        return f'{cls.type()}#{str(_id)}'
