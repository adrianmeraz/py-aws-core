import datetime
import random
from unittest import mock, TestCase

from py_aws_core import const, exceptions, utils


class BuildLambdaResponseTests(TestCase):

    def test_body_no_custom_headers(self):
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
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['application/json']
                }
            }
        )

    def test_text_plain_content_type(self):
        val = utils.build_lambda_response(
            status_code=200,
            body={'message': 'Lorem Ipsum'},
            content_type='text/plain;charset=utf-8',
        )
        self.assertEqual(
            val,
            {
                'isBase64Encoded': False,
                'statusCode': 200,
                'body': '{"message": "Lorem Ipsum"}',
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['text/plain;charset=utf-8'],
                }
            }
        )

    def test_headers(self):
        val = utils.build_lambda_response(
            status_code=200,
            body={'message': 'Lorem Ipsum'},
            multi_value_headers={
                'X-Request-Token': ['abcdefghijklmnopqrstuvwxyz1234567890'],
                'X-HMAC-Token': ['1234567890abcdefghijklmnopqrstuvwxyz']
            }
        )
        self.assertEqual(
            val,
            {
                'isBase64Encoded': False,
                'statusCode': 200,
                'body': '{"message": "Lorem Ipsum"}',
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['application/json'],
                    'X-Request-Token': ['abcdefghijklmnopqrstuvwxyz1234567890'],
                    'X-HMAC-Token': ['1234567890abcdefghijklmnopqrstuvwxyz']
                }
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
                'multiValueHeaders': {
                    'Access-Control-Allow-Credentials': [True],
                    'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
                    'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT'],
                    'Access-Control-Allow-Origin': ['*'],
                    'Content-Type': ['application/json']
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


class GenerateJitterTests(TestCase):
    def test_add_jitter(self):
        self.assertTrue(.5 <= utils.generate_jitter(midpoint=1.0, floor=0, std_deviation=.5) <= 1.5)
        self.assertTrue(11 <= utils.generate_jitter(midpoint=15.5, floor=11, std_deviation=20) <= 35.5)
        self.assertTrue(0.1437 <= utils.generate_jitter(midpoint=.156, floor=.07, std_deviation=.0123) <= 0.1683)


class AddDaysToUnixTimestampTests(TestCase):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_ok(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt
        val = utils.add_seconds_to_current_unix_timestamp(seconds=7*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1063380808)

        val = utils.add_seconds_to_current_unix_timestamp(seconds=180*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1078328008)


class DecodeStrTests(TestCase):
    def test_decode_str(self):
        val = utils.decode_unicode('ESPA\xc3\x91A')
        self.assertEqual(val, 'ESPAÑA')

        val = utils.decode_unicode('ESPAÑA')
        self.assertEqual(val, 'ESPAÑA')


class UnixTimestampToISO8601Tests(TestCase):
    def test_decode_str(self):
        val = utils.unix_timestamp_to_iso8601(1721535430)
        self.assertEqual(val, '2024-07-21T04:17:10+00:00')

        val = utils.unix_timestamp_to_iso8601(1220010000)
        self.assertEqual(val, '2008-08-29T11:40:00+00:00')


class RandIntTests(TestCase):
    @mock.patch.object(random, 'randint')
    def test_decode_str(self, mocked_randint):
        mocked_randint.return_value = 87

        val = utils.rand_int(num_a=10, num_b=99)
        self.assertEqual(val, 87)


class RemoveWhitespaceTests(TestCase):
    def test_ok(self):
        test_str = '{\\r\\n    "movement_type": "I",\\r\\n    "medium_transport_type": "A",\\r\\n    "flight_type": "C",\\r\\n    "control_point_id": "12",\\r\\n    "control_point_name": "MEDELLIN (MDE), AEROPUERTO JOSE MARIA CORDOVA",\\r\\n    "flight_date_yyyy_mm_dd": "2023-12-22",\\r\\n    "flight_number": "973",\\r\\n    "route_code": "10036",\\r\\n    "route_name": "FORTDERDALE-MEDELLIN",\\r\\n    "route_company_code": "SPR",\\r\\n    "route_company_name": "SPIRIT AIRLINES",\\r\\n    "country_id": "249",\\r\\n    "country_name": "ESTADOS UNIDOS",\\r\\n    "origin_city_id": "15",\\r\\n    "origin_city_department": "1",\\r\\n    "origin_city_name": "DALLAS , ESTADOS UNIDOS DE AMERICA"\\r\\n}'
        val = utils.remove_whitespace(test_str)
        self.assertEqual(val, '{"movement_type":"I","medium_transport_type":"A","flight_type":"C","control_point_id":"12","control_point_name":"MEDELLIN(MDE),AEROPUERTOJOSEMARIACORDOVA","flight_date_yyyy_mm_dd":"2023-12-22","flight_number":"973","route_code":"10036","route_name":"FORTDERDALE-MEDELLIN","route_company_code":"SPR","route_company_name":"SPIRITAIRLINES","country_id":"249","country_name":"ESTADOSUNIDOS","origin_city_id":"15","origin_city_department":"1","origin_city_name":"DALLAS,ESTADOSUNIDOSDEAMERICA"}')
