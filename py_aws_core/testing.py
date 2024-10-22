import json
import time
from http.cookiejar import Cookie
from importlib.abc import Traversable
from importlib.resources import as_file
from importlib.resources import files
from unittest import TestCase

import respx
from httpx import Response, codes

from py_aws_core import utils


class BaseTestFixture(TestCase):

    TEST_AUTH_TOKEN = 'eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6IjZmMjA5YzgyLWMyNTgtNGIzMC1hMGIxLTBjYWYwMDRkMDRkNiIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiJhMGNhODUwOS0xMTM0LTRmZWEtYTg5YS1kN2ZjYjRmOTg3ZTciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxMzY2NDMyMCwiZXhwIjoxNzEzNjY3OTIwLCJpYXQiOjE3MTM2NjQzMjAsImp0aSI6IjgzNGI3ZWYyLTBkN2EtNGM2My1hYjI1LWMxYjU1MTU5M2VhNiIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.HrlCeTFFfY_lKtA8HFFrzWRdyCdWbNdaMRozDH65Uzyy9FaavZq2enU8lQSs_TOyEl9aj5mxdIOmN03bpsaiZeWFLD6Ph_oUHl6MQBlgMGPQjzamAO6homn2IH-Thn5jcFdUVWEHIA4GHrw2M_Rty5sCDBxVkdjqCqU4KchoxL2zwXCGdp4Fr-p22PkG8bAkrLQAtO_QE2HqrseJo0XkOm64GDNVvNbL4O4EJ3NUY3vkRck2L0g0GMYG_1x8GFgwr1MdFOg0BOXvL4Qu0ToEVK86mjL-Ua8MR9t9Z4VraKIU5RSncm3SWuWTW6K2uo1oeXAXNWWhrA01Q3BeTGVvJg'
    TEST_RESOURCE_PATH = 'tests._resources'
    TEST_COGNITO_POOL_CLIENT_ID = '7xxxxtgbdebch6fffffueq2h1m'
    TEST_COGNITO_POOL_ID = 'us-west-2_CCCQW5ZZZ'
    TEST_ACCESS_TOKEN = 'eifuhwseduivfavhwveci'
    TEST_SESSION = 'AYABeFXvmcOOYfDt0FEXFF1YJU0AHQABAAdTZXJ2aWNlABBDb2duaXRvVXNlclBvb2xzAAEAB2F3cy1rbXMAS2Fybjphd3M6a21zOnVzLXdlc3QtMjowMTU3MzY3MjcxOTg6a2V5LzI5OTFhNGE5LTM5YTAtNDQ0Mi04MWU4LWRkYjY4NTllMTg2MQC4AQIBAHhPj7k9zU4nGXUQUvM0Ccwk42DS-fm3vKmH75ktTrktNQGm02KVuFeo-2uJN5UBn74vAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMV7Hs08X6HB6WKPsgAgEQgDuSOHzEU5wh_FikpJYjxXGPbYB3BC_fEDb05YWJnrokkGDf12Yrg53fxiUDNW7B523L2axIC7FT9tMShAIAAAAADAAAEAAAAAAAAAAAAAAAAADEdVndAEPLobnWu0H25hNC_____wAAAAEAAAAAAAAAAAAAAAEAAADT8xRI6YxhCSqev-6ZOdk2vuTmWFPCNGyhmbIKRG2yc2OVcWkuNYnX1neWZXYIFy4bmUseiL6_Bfr21wCg8JEnkgoNrc6crlRWSADrc3N7tVuPP_N_CbYPVX2_NurbuigG68m6mxWI9gXiep5W2OuqJWC_RUQlFrYvUDnMv0EiYHxxzBun7L3wG5uKa7UemhNbEU0UFKpLnbvFyT1Vk0UUzIIQVEalkHw7flr2cKthKoAAdHb1moJmGTxVPAG1FCrxqYL9C7HtKwOk2WLRuRw5_298fyLsJwRmR1CwM0L_S4IVor4'

    TEST_BOTO3_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('boto3')
    TEST_BOTO3_ERROR_RESOURCES_PATH = TEST_BOTO3_RESOURCES_PATH.joinpath('errors')

    TEST_COGNITO_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('cognito')
    TEST_COGNITO_ERROR_RESOURCES_PATH = TEST_COGNITO_RESOURCES_PATH.joinpath('errors')

    TEST_DB_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('db')
    TEST_DB_ERROR_RESOURCES_PATH = TEST_DB_RESOURCES_PATH.joinpath('errors')

    TEST_LAMBDA_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('lambda')
    TEST_LAMBDA_ERROR_RESOURCES_PATH = TEST_DB_RESOURCES_PATH.joinpath('errors')

    TEST_SECRETS_MANAGER_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('secrets_manager')
    # TEST_SECRETS_MANAGER_RESOURCES_PATH = TEST_DB_RESOURCES_PATH.joinpath('errors')

    TEST_SSM_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('ssm')

    def setUp(self):
        self.start_time = time.time()
        super().setUp()

    def tearDown(self):
        total = time.time() - self.start_time
        if total > 0.1:
            print(f'{self.id} slow test took {total:.3f} seconds')
        super().tearDown()

    @classmethod
    def create_ok_route(cls, method='GET', headers=None, _json=None, text=None, **kwargs):
        return cls.create_route(
            method=method,
            response_status_code=codes.OK,
            response_headers=headers,
            response_json=_json,
            response_text=text,
            **kwargs
        )

    @classmethod
    def create_bad_request_route(cls, **kwargs):
        return cls.create_route(response_status_code=codes.BAD_REQUEST, **kwargs)

    @classmethod
    def create_route(
        cls,
        response_status_code,
        method='GET',
        response_headers=None,
        response_json=None,
        response_text=None,
        **kwargs
    ):
        return respx.route(
            method=method,
            **kwargs
        ).mock(
            return_value=Response(
                headers=response_headers,
                status_code=response_status_code,
                json=response_json,
                text=response_text,
            )
        )

    @classmethod
    def create_test_cookie(cls, name: str, value: str) -> Cookie:
        return Cookie(
            version=1,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain='www.example.com',
            domain_specified=True,
            domain_initial_dot=False,
            path='/',
            path_specified=True,
            secure=True,
            expires=3600,
            discard=False,
            comment=None,
            comment_url=None,
            rest=dict(),
        )

    @classmethod
    def to_utf8_bytes(cls, s: str):
        return utils.to_utf8_bytes(s)

    @classmethod
    def get_resource_json(cls, *descendants: str, path: Traversable,):
        source = path.joinpath(*descendants)
        with as_file(source) as file_text:
            return json.loads(file_text.read_text(encoding='utf-8'))

    @classmethod
    def get_resource_text(cls, *descendants: str, path: Traversable):
        source = path.joinpath(*descendants)
        with as_file(source) as file_text:
            return file_text.read_text(encoding='utf-8')
