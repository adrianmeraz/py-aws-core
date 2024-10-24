from dataclasses import dataclass

import boto3
from boto3.dynamodb.table import TableResource
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from py_aws_core import const, logs, utils

logger = logs.get_logger()


class DynamoDBAPI:
    @dataclass
    class UpdateField:
        expression_attr: str
        set_once: bool = False

    @classmethod
    def build_update_expression(cls, fields: list[UpdateField]) -> str:
        n_fields = [f'#{f.expression_attr} = :{f.expression_attr}' for f in fields if not f.set_once]
        o_fields = [f'#{f.expression_attr} = if_not_exists(#{f.expression_attr}, :{f.expression_attr})' for f in fields
                    if f.set_once]
        return f'SET {', '.join(n_fields + o_fields)}'

    @classmethod
    def get_batch_entity_create_map(
        cls,
        pk: str,
        sk: str,
        _type: str,
        created_by: str = '',
        expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
        **kwargs,
    ) -> dict:
        return {
            'PK': pk,
            'SK': sk,
            'Type': _type,
            'CreatedAt': utils.to_iso_8601(),
            'CreatedBy': created_by,
            'ModifiedAt': '',
            'ModifiedBy': '',
            'ExpiresAt': cls.calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
        } | kwargs

    @classmethod
    def get_entity_update_map(
        cls,
        pk: str,
        sk: str,
        modified_by: str = '',
        **kwargs,
    ) -> dict:
        return {
            'PK': pk,
            'SK': sk,
            'ModifiedAt': utils.to_iso_8601(),
            'ModifiedBy': modified_by,
        } | kwargs

    @classmethod
    def get_put_item_map(
        cls,
        pk: str,
        sk: str,
        _type: str,
        created_by: str = '',
        expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
        **kwargs,
    ) -> dict:
        vals = {
           'PK': pk,
           'SK': sk,
           'Type': _type,
           'CreatedAt': utils.to_iso_8601(),
           'CreatedBy': created_by,
           'ModifiedAt': '',
           'ModifiedBy': '',
           'ExpiresAt': cls.calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
        } | kwargs
        return cls.serialize_types(vals)

    @classmethod
    def batch_write_item_maps(cls, table_resource: TableResource, item_maps: list[dict]) -> int:
        with table_resource.batch_writer() as batch:
            for _map in item_maps:
                batch.put_item(Item=_map)
        return len(item_maps)

    @classmethod
    def get_new_table_resource(cls, table_name: str):
        dynamodb_resource = boto3.resource('dynamodb')
        return dynamodb_resource.Table(table_name)

    @classmethod
    def serialize_types(cls, data: dict):
        """
        Converts normalized json to low level dynamo json
        """
        return {k: TypeSerializer().serialize(v) for k, v in data.items()}

    @classmethod
    def deserialize_types(cls, data: dict):
        """
        Converts low level dynamo json to normalized json
        """
        return {k: TypeDeserializer().deserialize(v) for k, v in data.items()}

    @classmethod
    def calc_expire_at_timestamp(cls, expire_in_seconds: int = None) -> int | str:
        """
        Adds seconds to current unix timestamp to generate new unix timestamp
        Seconds set to None will result in empty string
        :param expire_in_seconds: Seconds to add to current timestamp
        :return:
        """
        if expire_in_seconds is None:
            return ''
        return utils.add_seconds_to_current_unix_timestamp(seconds=expire_in_seconds)
