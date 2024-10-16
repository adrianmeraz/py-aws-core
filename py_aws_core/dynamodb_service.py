import typing

import boto3
from botocore.client import BaseClient

from py_aws_core import logs

logger = logs.get_logger()


class DynamoDBClient:
    """
        https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html
        If your primary key consists of both a partition key(pk) and a sort key(sk),
        the parameter will check whether attribute_not_exists(pk) AND attribute_not_exists(sk) evaluate to true or
        false before attempting the write operation.
    """
    def __init__(self, boto_client: BaseClient, dynamodb_table_name: str):
        self._boto_client = boto_client
        self._dynamodb_table_name = dynamodb_table_name
        self._table_resource = self.get_new_table_resource()

    def get_new_table_resource(self):
        resource = boto3.resource('dynamodb')
        return resource.Table(self._dynamodb_table_name)

    def query(self, *args, **kwargs):
        return self._boto_client.query(TableName=self._dynamodb_table_name, *args, **kwargs)

    def scan(self, *args, **kwargs):
        return self._boto_client.scan(TableName=self._dynamodb_table_name, *args, **kwargs)

    def get_item(self, *args, **kwargs):
        return self._boto_client.get_item(TableName=self._dynamodb_table_name, *args, **kwargs)

    def put_item(self, *args, **kwargs):
        return self._boto_client.put_item(TableName=self._dynamodb_table_name, *args, **kwargs)

    def delete_item(self, *args, **kwargs):
        return self._boto_client.delete_item(TableName=self._dynamodb_table_name, *args, **kwargs)

    def update_item(self, *args, **kwargs):
        return self._boto_client.update_item(TableName=self._dynamodb_table_name, *args, **kwargs)

    def batch_write_item(self, *args, **kwargs):
        return self._boto_client.batch_write_item(*args, **kwargs)

    def transact_write_items(self, *args, **kwargs):
        return self._boto_client.transact_write_items(*args, **kwargs)

    def batch_write_item_maps(self, item_maps: typing.List[typing.Dict]) -> int:
        with self._table_resource.batch_writer() as batch:
            for _map in item_maps:
                batch.put_item(Item=_map)
        return len(item_maps)
