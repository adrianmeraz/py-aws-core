import json
from importlib.resources import as_file
from unittest import TestCase, mock

from botocore.exceptions import ClientError
from httpx import HTTPStatusError, Request, Response

from py_aws_core import decorators, exceptions
from tests import const as test_const


class Boto3Tests(TestCase):

    def test_no_exception(self):
        @decorators.boto3_handler(raise_as=RuntimeError, client_error_map=dict())
        def func(x):
            return 2 * x

        val = func(7)
        self.assertEqual(
            14,
            val
        )

    def test_raise_mapped_client_error(self):
        source = test_const.TEST_BOTO3_ERROR_RESOURCES_PATH.joinpath('client_error.json')
        with as_file(source) as err_json:
            err_json = json.loads(err_json.read_text(encoding='utf-8'))
            client_error = ClientError(error_response=err_json, operation_name='test1')

        client_err_map = {
            'SomeServiceException': ArithmeticError
        }

        @decorators.boto3_handler(raise_as=RuntimeError, client_error_map=client_err_map)
        def func():
            raise client_error
        with self.assertRaises(ArithmeticError):
            func()

    def test_raise_unmapped_client_error(self):
        source = test_const.TEST_BOTO3_ERROR_RESOURCES_PATH.joinpath('client_error.json')
        with as_file(source) as err_json:
            err_json = json.loads(err_json.read_text(encoding='utf-8'))
            client_error = ClientError(error_response=err_json, operation_name='test1')

        client_err_map = {
            'OtherException': ArithmeticError
        }

        @decorators.boto3_handler(raise_as=RuntimeError, client_error_map=client_err_map)
        def func():
            raise client_error
        with self.assertRaises(RuntimeError):
            func()

    def test_reraise_uncaught_exception(self):
        @decorators.boto3_handler(raise_as=RuntimeError, client_error_map=dict())
        def func():
            raise KeyError
        with self.assertRaises(KeyError):
            func()


class DynamodbHandlerTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_err_map = {
            'SomeServiceException': ArithmeticError
        }

    def test_no_exception(self):
        @decorators.dynamodb_handler(client_err_map=self.client_err_map, cancellation_err_maps=list(dict()))
        def func(x):
            return 2 * x

        val = func(7)
        self.assertEqual(
            14,
            val,
        )

    def test_raise_client_error(self):
        source = test_const.TEST_BOTO3_ERROR_RESOURCES_PATH.joinpath('client_error.json')
        with as_file(source) as err_json:
            err_json = json.loads(err_json.read_text(encoding='utf-8'))
            client_error = ClientError(error_response=err_json, operation_name='test1')

        @decorators.dynamodb_handler(client_err_map=self.client_err_map, cancellation_err_maps=list())
        def func():
            raise client_error
        with self.assertRaises(ArithmeticError):
            func()

    def test_raise_cancellation_error(self):
        source = test_const.TEST_BOTO3_ERROR_RESOURCES_PATH.joinpath('client_error#ConditionalCheckFailed.json')
        with as_file(source) as initiate_auth_json:
            err_json = json.loads(initiate_auth_json.read_text(encoding='utf-8'))
            client_error = ClientError(error_response=err_json, operation_name='test1')

        cancellation_error_maps = [
            {
                'ConditionalCheckFailed': RuntimeError
            }
        ]

        @decorators.dynamodb_handler(client_err_map=dict(), cancellation_err_maps=cancellation_error_maps)
        def func():
            raise client_error
        with self.assertRaises(RuntimeError):
            func()


class HttpStatusCheckTests(TestCase):

    def test_check_response_no_reraise(self):
        request = Request(url='', method='')
        func = mock.Mock(side_effect=HTTPStatusError(
            request=request,
            response=Response(
                request=request,
                status_code=400,
            ),
            message='test'
        ))
        decorated_function = decorators.http_status_check(reraise_status_codes=())(func)
        with self.assertRaises(exceptions.APIException):
            decorated_function()

    def test_check_response_reraise(self):
        request = Request(url='', method='')
        func = mock.Mock(side_effect=HTTPStatusError(
            request=request,
            response=Response(
                request=request,
                status_code=502,
            ),
            message='test'
        ))
        decorated_function = decorators.http_status_check(reraise_status_codes=(500, 501, 502))(func)
        with self.assertRaises(HTTPStatusError):
            decorated_function()


class LambdaResponseHandlerTests(TestCase):

    def test_no_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.DynamoDBException)
        def func(x):
            return 2*x
        val = func(7)
        self.assertEqual(
            14,
            val
        )

    def test_pass_thru_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.DynamoDBException)
        def func():
            raise exceptions.DBConditionCheckFailed('This is a test')
        val = func()
        self.assertEqual(
            {
                'body': '{"error": "DBConditionCheckFailed: Condition Check Failed"}',
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['application/json']
                },
                'isBase64Encoded': False,
                'statusCode': 400
            },
            val
        )

    def test_wrapped_exception(self):
        @decorators.lambda_response_handler(raise_as=exceptions.CoreException)
        def func():
            raise RuntimeError('This is a test')
        val = func()
        self.assertEqual(
            {
                'body': '{"error": "CoreException: A generic error has occurred"}',
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['application/json']
                },
                'isBase64Encoded': False,
                'statusCode': 400
            },
            val
        )


class RetryTests(TestCase):
    def test_multi_retry(self):
        tries = 7

        func = mock.Mock(side_effect=exceptions.CoreException("Test"))
        decorated_function = decorators.retry(
            retry_exceptions=(exceptions.CoreException,),
            tries=tries,
            delay=0,
            backoff=1,
            jitter=0,
        )(func)
        with self.assertRaises(exceptions.CoreException):
            decorated_function()
        self.assertEqual(func.call_count, tries)

    def test_single_retry(self):
        tries = 1
        func = mock.Mock(side_effect=exceptions.CoreException("Test"))
        decorated_function = decorators.retry(
            retry_exceptions=(exceptions.CoreException,),
            tries=tries,
            delay=0,
            backoff=1,
            jitter=0,
        )(func)
        with self.assertRaises(exceptions.CoreException):
            decorated_function()
        self.assertEqual(func.call_count, tries)


class WrapExceptions(TestCase):
    def test_no_exception(self):
        @decorators.wrap_exceptions(raise_as=BlockingIOError)
        def func(x):
            return 2 * x

        val = func(7)
        self.assertEqual(
            val,
            14
        )

    def test_pass_thru(self):
        @decorators.wrap_exceptions(raise_as=BlockingIOError)
        def func():
            raise BlockingIOError

        with self.assertRaises(BlockingIOError):
            func()

    def test_catch_all(self):
        @decorators.wrap_exceptions(raise_as=BlockingIOError)
        def func():
            raise KeyError

        with self.assertRaises(BlockingIOError):
            func()
