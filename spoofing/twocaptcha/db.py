import typing
import uuid

from py_aws_core import decorators as aws_decorators, encoders, entities, exceptions
from py_aws_core.db_dynamo import ABCCommonAPI, DDBClient, QueryResponse
from py_aws_core.mixins import JsonMixin

from . import entities

__db_client = DDBClient()


def get_db_client():
    """
    Reuses db client across all modules for efficiency
    :return:
    """
    return __db_client


class CMDBAPI(ABCCommonAPI):
    """
    https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html
    If your primary key consists of both a partition key(pk) and a sort key(sk),
    the parameter will check whether attribute_not_exists(pk) AND attribute_not_exists(sk) evaluate to true or
    false before attempting the write operation.
    """
    CANCELLATION_ERROR_MAPS = []

    @classmethod
    def build_recaptcha_event_map(
        cls,
        _id: uuid.UUID,
        text: str,
        value: str,
    ):
        # TODO Add rest of fields
        pk = sk = entities.RecaptchaEvent.create_key(_id)
        return cls.get_batch_entity_create_map(
            expire_in_seconds=None,
            pk=pk,
            sk=sk,
            _type=entities.RecaptchaEvent.type(),
            Text=text,
            Value=value
        )
