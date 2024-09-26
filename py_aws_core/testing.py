import json
import time
from http.cookiejar import Cookie
from importlib.abc import Traversable
from importlib.resources import as_file
from unittest import TestCase

import respx
from httpx import Response, codes

from py_aws_core import utils


class BaseTestFixture(TestCase):
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
