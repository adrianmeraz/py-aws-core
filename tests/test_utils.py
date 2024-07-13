import datetime
from unittest import mock, TestCase

from py_aws_core import exceptions, utils


class BuildLambdaResponseTests(TestCase):

    def test_body(self):
        val = utils.build_lambda_response(
            status_code=200,
            body={'message': 'Lorem Ipsum'}
        )
        self.assertEqual(
            val,
            {
                'isBase64Encoded': False,
                'statusCode': 200,
                'body': '{"message": "Lorem Ipsum"}',
                'headers': {
                    'Access-Control-Allow-Credentials': True,
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,POST,PUT',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'}
            }
        )

    def test_exception(self):
        val = utils.build_lambda_response(
            status_code=400,
            exc=exceptions.SecretsManagerException("Lorem Ipsum")
        )
        self.assertEqual(
            val,
            {
                'isBase64Encoded': False,
                'body': '{"error": "SecretsManagerException: An error occurred while fetching secrets"}',
                'headers': {
                    'Access-Control-Allow-Credentials': True,
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,POST,PUT',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'statusCode': 400,
            }
        )


class Iso8601NowTimestampTests(TestCase):
    def test_ok(self):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28)
        val = utils.to_iso_8601(dt=dt)
        self.assertEqual(
            val,
            '2003-09-05T15:33:28'
        )


class AddDaysToUnixTimestampTests(TestCase):
    @mock.patch.object(utils, 'get_now_timestamp')
    def test_ok(self, mocked_get_now_timestamp):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28)
        mocked_get_now_timestamp.return_value = dt
        val = utils.add_days_to_unix_timestamp(days=7)
        self.assertEqual(val, 1063398808)

        val = utils.add_days_to_unix_timestamp(days=180)
        self.assertEqual(val, 1078349608)
