from boto3.dynamodb import types

from . import encoders


class BaseModel:
    def __init__(self, data):
        self.__data = self.to_normalized_data(data)
        self.PK = self.data['PK']
        self.SK = self.data['SK']
        self.Type = self.data['Type']
        self.CreatedAt = self.data['CreatedAt']
        self.CreatedBy = self.data.get('CreatedBy')
        self.ModifiedAt = self.data.get('ModifiedAt')
        self.ModifiedBy = self.data.get('ModifiedBy')

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
