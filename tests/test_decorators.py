from unittest import TestCase
from py_aws_core import decorators, exceptions


class DynamodbHandlerTests(TestCase):
    pass


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
