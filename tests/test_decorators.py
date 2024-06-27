import json
from importlib.resources import as_file
from unittest import TestCase

from botocore.exceptions import ClientError

from py_aws_core import decorators, exceptions
from tests import const as test_const


class DynamodbHandlerTests(TestCase):
    def test_no_exception(self):
        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=list(dict()))
        def func(x):
            return 2 * x

        val = func(7)
        self.assertEqual(
            val,
            14
        )

    def test_raise_client_error(self):
        source = test_const.TEST_BOTO3_ERROR_RESOURCES_PATH.joinpath('client_error#ConditionalCheckFailed.json')
        with as_file(source) as initiate_auth_json:
            err_json = json.loads(initiate_auth_json.read_text())
            client_error = ClientError(error_response=err_json, operation_name='test1')

        CANCELLATION_ERROR_MAPS = [
            {
                'ConditionalCheckFailed': RuntimeError
            }
        ]

        @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=CANCELLATION_ERROR_MAPS)
        def func():
            raise client_error
        with self.assertRaises(RuntimeError):
            func()


class LambdaResponseHandlerTests(TestCase):

    def test_no_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.DynamoDBException)
        def func(x):
            return 2*x
        val = func(7)
        self.assertEqual(
            val,
            14
        )

    def test_pass_thru_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.DynamoDBException)
        def func():
            raise exceptions.DBConditionCheckFailed('This is a test')
        val = func()
        self.assertEqual(
            val,
            {
                'body': '{"error": "DBConditionCheckFailed: Condition Check Failed"}',
                'headers': {
                    'Access-Control-Allow-Credentials': True,
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,POST,PUT',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'isBase64Encoded': False,
                'statusCode': 400
            }
        )

    def test_wrapped_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.AWSCoreException)
        def func():
            raise RuntimeError('This is a test')
        val = func()
        self.assertEqual(
            val,
            {
                'body': '{"error": "AWSCoreException: A generic error has occurred"}',
                'headers': {
                    'Access-Control-Allow-Credentials': True,
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,POST,PUT',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'isBase64Encoded': False,
                'statusCode': 400
            }
        )
